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

    for path in sorted((I18N_DIR / 'translations').glob('*.json')):
        with open(path, encoding='utf-8') as file:
            entries = json.load(file)

        for i, entry in enumerate(entries):
            if not entry:
                continue
            try:
                xml.fromstring(f'<t>{entry["message"]}</t>')
            except xml.ParseError as exc:
                print(f'{path.name}[{i}] ({entry["name"]}): {exc}', file=sys.stderr)
                errors += 1

    if errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
