#!/usr/bin/env python3
# Copyright 2026 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""
Apply translated strings into Chromium XTB files.
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as xml
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import name_substitution_utils as namesub

REPO_ROOT = Path(__file__).resolve().parent.parent
I18N_DIR = REPO_ROOT / 'i18n'
SOURCE_PATH = I18N_DIR / 'source.gen.json'
TRANSLATIONS_DIR = I18N_DIR / 'translations'


def get_id(name, context, text):
    """Compute the fingerprint ID for a GRD message element."""
    message = xml.fromstring(f'<message name="{name}" desc="{context}">{text}</message>')
    return namesub.compute_fp(message)


def find_parent_grd(tree, grdp_path):
    """Find the parent GRD that includes a GRDP via <part file="...">."""
    grdp_name = Path(grdp_path).name
    grd_dir = tree / Path(grdp_path).parent
    for grd_file in grd_dir.glob('*.grd'):
        root = xml.parse(grd_file).getroot()
        for part in root.iter('part'):
            if part.get('file') == grdp_name:
                return grd_file
    raise FileNotFoundError(f'no parent GRD found for {grdp_path}')


def get_parent_grd(tree, source_path):
    """Get the parent GRD file for a source path (GRD or GRDP)."""
    if source_path.endswith('.grd'):
        return tree / source_path
    return find_parent_grd(tree, source_path)


def parse_xtb_paths(grd_path):
    """Parse a GRD file and return a dict of lang -> XTB path."""
    grd_dir = grd_path.parent
    root = xml.parse(grd_path).getroot()
    result = {}
    for node in root.iter('file'):
        path = node.get('path', '')
        if path.endswith('.xtb'):
            result[node.get('lang')] = grd_dir / path
    return result


def to_xtb_message(message):
    """Convert a GRD-style message to XTB format."""
    return re.sub(
        r'<ph name="([^"]+)">.*?</ph>',
        r'<ph name="\1" />',
        message,
    )


def insert_into_xtb(xtb_path, translations):
    """Insert or update <translation> elements in an XTB file."""
    content = xtb_path.read_text(encoding='utf-8')
    parser = xml.XMLParser(target=xml.TreeBuilder(insert_comments=True))
    root = xml.fromstring(content, parser)

    existing_ids = {}
    for node in root.findall('.//translation'):
        existing_ids[node.get('id')] = node

    for msg_id, message in translations:
        if msg_id in existing_ids:
            node = existing_ids[msg_id]
            node.text = message
            # clear any children (old ph tags) and re-parse
            for child in list(node):
                node.remove(child)
        else:
            node = xml.SubElement(root, 'translation')
            node.set('id', msg_id)

        # parse the message to get mixed content (text + <ph> elements)
        wrapped = f'<t>{message}</t>'
        parsed = xml.fromstring(wrapped)
        node.text = parsed.text
        for child in parsed:
            node.append(child)
            child.tail = child.tail or ''
        if not node.tail:
            node.tail = '\n'

    xtb_path.write_text(
        xml.tostring(root, encoding='unicode', xml_declaration=True),
        encoding='utf-8',
    )


def build_xtb_index(source, tree):
    """Prebuild a mapping from source path -> {lang -> XTB path}."""
    grd_cache = {}
    index = {}
    for src in source:
        src_path = src['source']
        if src_path in index:
            continue
        grd_path = get_parent_grd(tree, src_path)
        grd_key = str(grd_path)
        if grd_key not in grd_cache:
            grd_cache[grd_key] = parse_xtb_paths(grd_path)
        index[src_path] = grd_cache[grd_key]
    return index


def resolve_xtb(src, lang_code, xtb_index):
    """Resolve which XTB file a source entry maps to for a given language."""
    xtb_map = xtb_index[src['source']]
    # nb is listed as "no" in XTB files
    xtb_lang = 'no' if lang_code == 'nb' else lang_code
    return xtb_map.get(xtb_lang)


def merge_into_xtb(xtb_path, source_entries, trans_by_key):
    """Merge translations for matching source entries into a single XTB file."""
    # TODO: handle feminine/masculine variants via <branch> elements
    seen_ids = set()
    entries = []
    for src in source_entries:
        key = (src['name'], src['message'])
        trans = trans_by_key.get(key)
        if not trans:
            continue
        msg_id = get_id(src['name'], src['context'], src['message'])
        if msg_id in seen_ids:
            continue
        seen_ids.add(msg_id)
        entries.append((msg_id, to_xtb_message(trans['message'])))

    if entries:
        insert_into_xtb(xtb_path, entries)
    return len(entries)


def apply_language(task):
    """Apply translations for a single language into XTB files."""
    lang_code, source, xtb_index = task
    trans_path = TRANSLATIONS_DIR / f'{lang_code}.json'
    if not trans_path.exists():
        print(f'{lang_code}: no translations found, skipping', file=sys.stderr)
        return

    with open(trans_path, encoding='utf-8') as f:
        translations = json.load(f)

    trans_by_key = {}
    for trans in translations:
        if trans:
            trans_by_key[(trans['name'], trans['source'])] = trans

    # group source entries by target XTB file
    by_xtb = defaultdict(list)
    for src in source:
        xtb_path = resolve_xtb(src, lang_code, xtb_index)
        if not xtb_path:
            raise FileNotFoundError(f'no XTB file for lang {lang_code} '
                                    f'in GRD for {src["source"]}')
        by_xtb[xtb_path].append(src)

    total = 0
    for xtb_path, source_entries in by_xtb.items():
        total += merge_into_xtb(xtb_path, source_entries, trans_by_key)

    print(f'{lang_code}: applied {total} translations to {len(by_xtb)} XTB files')


def main():
    """CLI entrypoint"""
    parser = argparse.ArgumentParser(description='Apply i18n translations to Chromium XTB files')
    parser.add_argument('-t',
                        '--tree',
                        type=Path,
                        required=True,
                        help='Path to Chromium source tree')
    args = parser.parse_args()

    with open(SOURCE_PATH, encoding='utf-8') as f:
        source = json.load(f)
    with open(I18N_DIR / 'languages.json', encoding='utf-8') as f:
        languages = json.load(f)

    namesub.add_grit_to_path(args.tree)
    xtb_index = build_xtb_index(source, args.tree)

    tasks = [(code, source, xtb_index) for code in languages]
    with Pool() as pool:
        pool.map(apply_language, tasks)


if __name__ == '__main__':
    sys.exit(main())
