# Copyright 2026 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Helper for cleaning up obsolete and outdated translation strings."""

import json
from pathlib import Path

from i18n_titlecase import (
    build_title_case_aliases,
    source_key,
    translation_key,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
I18N_DIR = REPO_ROOT / 'i18n'
SOURCE_PATH = I18N_DIR / 'source.gen.json'
TRANSLATIONS_DIR = I18N_DIR / 'translations'


def clean_translation_file(lang, source_keys, translation_aliases):
    """Clean up outdated and duplicated translations in a language file."""
    path = TRANSLATIONS_DIR / f'{lang}.json'
    with open(path, encoding='utf-8') as file:
        entries = json.load(file)

    result_indices = {}
    result_has_alias = {}
    result = []
    n_filtered = 0
    changed = False
    for entry in entries:
        key = translation_key(entry, translation_aliases)
        if key not in source_keys:
            n_filtered += 1
            changed = True
            continue

        entry = dict(entry)
        is_alias = entry['source'] != key[1]
        if is_alias:
            entry['source'] = key[1]
            changed = True

        if key not in result_indices:
            result_indices[key] = len(result)
            result_has_alias[key] = is_alias
            result.append(entry)
        else:
            if result_has_alias[key] and not is_alias:
                result[result_indices[key]] = entry
                result_has_alias[key] = False
            n_filtered += 1
            changed = True

    if changed:
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

    source_aliases, translation_aliases = build_title_case_aliases(source)
    existing_keys = {source_key(entry, source_aliases) for entry in source}

    for lang in languages:
        n_filtered = clean_translation_file(lang, existing_keys, translation_aliases)
        if n_filtered:
            print(f'{lang}: filtered {n_filtered} string(s)')
