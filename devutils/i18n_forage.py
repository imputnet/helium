# Copyright 2026 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Helper for finding existing translated strings in upstream Chromium."""

import sys
import json
from pathlib import Path
from collections import defaultdict
import xml.etree.ElementTree as xml

I18N_DIR = Path(__file__).resolve().parent.parent / 'i18n'
SOURCE_PATH = I18N_DIR / 'source.gen.json'
TRANSLATIONS_DIR = I18N_DIR / 'translations'

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'utils'))
from i18n_apply import get_id, build_xtb_index, resolve_xtb
import name_substitution_utils as namesub


def get_untranslated_strings_by_xtb(source, lang, xtb_index):
    """Generates a map of xtb_path -> [untranslated strings]."""
    translation_path = TRANSLATIONS_DIR / f'{lang}.json'
    trans_keys = set()

    if translation_path.exists():
        with open(translation_path, encoding='utf-8') as file:
            translations = json.load(file)
        for translation in translations:
            trans_keys.add((translation['name'], translation['source']))

    filtered = defaultdict(list)
    for string in source:
        xtb_file = resolve_xtb(string, lang, xtb_index)
        assert xtb_file is not None
        if (string['name'], string['message']) not in trans_keys:
            filtered[xtb_file].append(string)
    return filtered


def to_fpmap(strings):
    """Generates a fingerprint -> source string mapping."""
    fp_map = {}
    for string in strings:
        fingerprint = get_id(string['name'], string['context'], string['message'],
                             string.get('meaning'))
        fp_map[fingerprint] = string
    return fp_map


def stringify_inner_xml(node):
    """Takes an XML node and stringifies its inner contents."""
    parts = [node.text or '']
    for child in node:
        parts.append(xml.tostring(child, encoding='unicode'))
    return ''.join(parts)


def find_matching(path, fpmap):
    """Finds pre-existing matching translations for Helium strings."""
    content = path.read_text(encoding='utf-8')
    root = xml.fromstring(content)

    out = {}
    for node in root.findall('.//translation'):
        fingerprint = node.get('id')
        if fingerprint in fpmap:
            out[fingerprint] = stringify_inner_xml(node)
    return out


def apply_matching(lang, matching, fpmap):
    """
    Takes a map of found matches and applies them to the helium i18n file.
    """
    translation_path = TRANSLATIONS_DIR / f'{lang}.json'
    translations = []
    if translation_path.exists():
        with open(translation_path, encoding='utf-8') as file:
            translations = json.load(file)

    for fingerprint, translation in matching.items():
        original = fpmap[fingerprint]
        translations.append({
            'name': namesub.replace_text(original['name'])[0],
            'source': namesub.replace_text(original['message'])[0],
            'message': namesub.replace_text(translation)[0],
        })

    with open(translation_path, 'w', encoding='utf-8') as file:
        json.dump(translations, file, indent=2, ensure_ascii=False)
        file.write('\n')


def run(args):
    """Forages for usable existing Chromium translations."""
    with open(SOURCE_PATH, encoding='utf-8') as file:
        source = json.load(file)
    with open(I18N_DIR / 'languages.json', encoding='utf-8') as file:
        languages = json.load(file)

    namesub.add_grit_to_path(args.tree)
    xtb_map = build_xtb_index(source, args.tree)

    for lang in languages:
        missing = get_untranslated_strings_by_xtb(source, lang, xtb_map)
        for path, strings in missing.items():
            fpmap = to_fpmap(strings)
            matching = find_matching(path, fpmap)
            if matching:
                apply_matching(lang, matching, fpmap)
