# Copyright 2025 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Util library for name_substitution.py"""

import re
import sys
import xml.etree.ElementTree as xml

REPLACEMENT_REGEXES_STR = [
    # stuff we don't want to replace
    (r'(\w+) Root Program', r'\1_unreplace Root Program'),
    (r'(\w+) Web( S|s)tore', r'\1_unreplace Web Store'),
    (r'(\w+) Remote Desktop', r'\1_unreplace Remote Desktop'),
    (r'("BEGIN_LINK_CHROMIUM")(.*?Chromium)(.*?<ph name="END_LINK_CHROMIUM")', r'\1\2_unreplace\3'),

    # main replacement(s)
    (r'(\b)chrome://', r'\1helium://'),
    (r'(?:Google )?Chrom(e|ium)(?!\w)', r'Helium'),

    # post-replacement cleanup
    (r'((?:Google )?Chrom(e|ium))_unreplace', r'\1'),
    (r'_unreplace', r'')
]

REPLACEMENT_REGEXES = list(map(lambda line: (re.compile(line[0]), line[1]),
                               REPLACEMENT_REGEXES_STR))


def add_grit_to_path(tree):
    """Inserts the grit/ folder into the module loading path."""
    grit_path = tree / 'tools' / 'grit'
    if not grit_path.exists():
        raise FileNotFoundError(f"grit directory not found at {grit_path}")
    sys.path.insert(0, str(grit_path))


def strip_message_text_for_fp(text):
    """
    Removes whitespace markers from GRIT text.
    See for example: IDS_EXTENSIONS_SETTINGS_API_SECOND_LINE_START_PAGES
    in //chrome/app/chromium_strings.grd.
    """
    text = text.strip()
    if text.startswith("'''"):
        text = text[3:]
    if text.endswith("'''"):
        text = text[:-3]
    return text.strip()


def compute_fp(message):
    """
    Computes the fingerprint for a particular .grd <message>, which is
    later used to replace the fingerprints used in .xtb l10n files.
    """
    # We need to import this here, because it only becomes
    # available after add_grit_to_path() is called.
    # pylint: disable=import-outside-toplevel,import-error
    import grit.extern.tclib

    text = message.text or ''
    for elem in message.findall('ph'):
        text = text + elem.get('name').upper() + (elem.tail or '')
    text = strip_message_text_for_fp(text)

    meaning = message.get('meaning', '')
    return grit.extern.tclib.GenerateMessageId(text, meaning)


def replace_text(text):
    """Replaces instances of Chrom(e | ium) with Helium in strings"""
    had_match = False
    for regex, replacement in REPLACEMENT_REGEXES:
        if regex.search(text):
            had_match = True
            text = regex.sub(replacement, text)

    return text, had_match


def replace_grit_message(msg):
    """
    Replaces instances of Chrom(e | ium) with Helium
    in a <message> or <translation> element (and its children).
    """
    had_any_match = False

    if msg.text:
        text, match = replace_text(msg.text)
        msg.text = text
        had_any_match |= match

    if msg.tail:
        tail, match = replace_text(msg.tail)
        msg.tail = tail
        had_any_match |= match

    for child in msg:
        had_any_match |= replace_grit_message(child)

    return had_any_match


def replace_xtb_translation(msg, fp_map):
    """
    Replaces instances of Chrom(e | ium) with Helium in a
    .xtb <translation>.
    """
    if not replace_grit_message(msg):
        return False

    msg_id = msg.get('id')
    if msg_id in fp_map:
        msg.set('id', fp_map[msg_id])
    return True


def replace_grit_tree(text):
    """Replaces instances of Chrom(e | ium) with Helium, where desired"""
    xml_tree = xml.fromstring(text)
    fp_map = {}

    for message in xml_tree.findall('.//message'):
        old_fp = compute_fp(message)
        if replace_grit_message(message):
            new_fp = compute_fp(message)
            fp_map[old_fp] = new_fp

    return xml.tostring(xml_tree, encoding='unicode'), fp_map


def replace_xtb_tree(text, fp_map):
    """Same as replace_grit_tree(), but on .xtb translation files."""
    xml_tree = xml.fromstring(text)
    changed = False

    for translation in xml_tree.findall('.//translation'):
        assert translation.get('id')
        changed |= replace_xtb_translation(translation, fp_map)

    if changed:
        return xml.tostring(xml_tree, encoding='unicode')

    return None


def merge_fp_maps(results):
    """
    Takes all the results from substitute_file() calls, and merges
    their fingerprint mappings.
    """
    merged_fp_map = {}
    for result in results:
        if result is None:
            continue
        _, fp_map = result
        merged_fp_map.update(fp_map)
    return merged_fp_map
