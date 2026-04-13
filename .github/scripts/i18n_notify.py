#!/usr/bin/env python3
# Copyright 2026 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Resolve translation file owners for notification."""

import sys
import yaml


def main():
    """Read changed files from stdin, print mention comment."""
    with open('i18n/owners.yml', encoding='utf-8') as file:
        owners = yaml.safe_load(file).get('owners', {})

    mentions = set()
    for line in sys.stdin:
        path = line.strip()
        if not path or not path.endswith('.json'):
            continue
        if '/translations/' not in path:
            continue
        lang = path.split('/')[-1].removesuffix('.json')
        for user in owners.get(lang, []):
            mentions.add(f'@{user}')

    if mentions:
        print('Translation review requested: ' + ' '.join(sorted(mentions)))


if __name__ == '__main__':
    main()
