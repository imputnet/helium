# Copyright 2026 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Helper for cleaning up obsolete and outdated translation strings."""

import json
from pathlib import Path

I18N_DIR = Path(__file__).resolve().parent.parent / 'i18n'
SOURCE_PATH = I18N_DIR / 'source.gen.json'
TRANSLATIONS_DIR = I18N_DIR / 'translations'


def clean_translation_file(lang, source_keys):
    """Clean up outdated and duplicated translations in a language file."""
    path = TRANSLATIONS_DIR / f'{lang}.json'
    with open(path, encoding='utf-8') as file:
        entries = json.load(file)

    translation_keys = set()
    result = []
    n_filtered = 0
    for entry in entries:
        key = (entry['name'], entry['source'])
        if key in source_keys and key not in translation_keys:
            result.append(entry)
            translation_keys.add(key)
        else:
            n_filtered += 1

    if n_filtered > 0:
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(result, file, indent=2, ensure_ascii=False)
            file.write('\n')

    return n_filtered


def run():
    """Clean up outdated translation strings."""
    with open(SOURCE_PATH, encoding='utf-8') as file:
        source = json.load(file)
    with open(I18N_DIR / 'languages.json', encoding='utf-8') as file:
        languages = json.load(file)

    existing_keys = set()
    for entry in source:
        existing_keys.add((entry['name'], entry['message']))

    for lang in languages:
        n_filtered = clean_translation_file(lang, existing_keys)
        if n_filtered:
            print(f'{lang}: filtered {n_filtered} string(s)')
