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


def main():
    """Validate all translation files."""
    errors = 0

    with open(I18N_DIR / 'source.gen.json', encoding='utf-8') as file:
        source = json.load(file)
    source_keys = {(s['name'], s['message']) for s in source}

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
            if key not in source_keys:
                print(f'{path.name}[{i}] ({entry["name"]}): '
                      f'no matching source string',
                      file=sys.stderr)
                errors += 1

    if errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
