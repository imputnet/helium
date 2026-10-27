#!/usr/bin/env python3
# Copyright 2026 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Validate i18n translation files."""

import json
import sys
import xml.etree.ElementTree as xml
from pathlib import Path

I18N_DIR = Path(__file__).resolve().parent.parent / 'i18n'

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'utils'))
from i18n_apply import to_xtb_message # pylint: disable=wrong-import-position

sys.path.pop(0)


def get_placeholders(root):
    """Return placeholder names and argument bindings, ignoring their order."""
    return sorted((node.get('name'), node.text) for node in root.iter('ph'))


def validate_placeholders(source_message, translated_message):
    """Validate placeholders before and after conversion to XTB syntax."""
    errors = []
    source_root = xml.fromstring(f'<t>{source_message}</t>')
    translated_root = xml.fromstring(f'<t>{translated_message}</t>')
    expected = get_placeholders(source_root)

    if get_placeholders(translated_root) != expected:
        errors.append('translation placeholders do not match source')

    converted_root = xml.fromstring(f'<t>{to_xtb_message(translated_message)}</t>')
    converted = get_placeholders(converted_root)
    expected_converted = sorted((name, None) for name, _value in expected)
    if converted != expected_converted:
        errors.append('XTB conversion changed placeholders')

    return errors


def main():
    """Validate all translation files."""
    errors = 0

    with open(I18N_DIR / 'source.gen.json', encoding='utf-8') as file:
        source = json.load(file)
    source_by_key = {(s['name'], s['message']): s for s in source}

    for path in sorted((I18N_DIR / 'translations').glob('*.json')):
        with open(path, encoding='utf-8') as file:
            entries = json.load(file)

        for i, entry in enumerate(entries):
            if not entry:
                continue
            try:
                xml.fromstring(f'<t>{entry["message"]}</t>')
            except xml.ParseError as exc:
                print(f'{path.name}[{i}] ({entry["name"]}): invalid xml: {exc}', file=sys.stderr)
                errors += 1
                continue

            key = (entry['name'], entry['source'])
            source_entry = source_by_key.get(key)
            if source_entry is None:
                print(f'{path.name}[{i}] ({entry["name"]}): '
                      f'no matching source string',
                      file=sys.stderr)
                errors += 1
                continue

            for error in validate_placeholders(source_entry['message'], entry['message']):
                print(f'{path.name}[{i}] ({entry["name"]}): {error}', file=sys.stderr)
                errors += 1

    if errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
