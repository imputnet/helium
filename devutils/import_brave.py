#!/usr/bin/env python3
# Copyright 2026 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Copies files from brave-core, unmodified, into the top quilt patch."""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

_PREFIX = 'brave/'
_REV_LINE = re.compile(r'^brave-core: ([0-9a-f]{40})$', re.MULTILINE)

# Tests need brave's test harness.
_SKIPPED = re.compile(r'(^|/)(test|android|ios)/|_(unit|browser)?tests?\.|'
                      r'_test_(utils|api|support)|(^|/)mock_|\.(md|java|swift)$')


def _quilt(*args, stdin=None):
    return subprocess.run(['quilt', '--quiltrc', '-', *args],
                          check=True,
                          input=stdin,
                          stdout=subprocess.PIPE,
                          text=True).stdout


def _git(brave_core, *args):
    return subprocess.run(['git', '-C', brave_core, *args], check=True,
                          stdout=subprocess.PIPE).stdout


def main():
    """Vendors the given paths, or updates the vendored files to --rev"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--brave-core', required=True, help='path to a brave-core checkout')
    parser.add_argument('--rev', help='brave-core commit (default: the one in the patch header)')
    parser.add_argument('paths', nargs='*', help='brave-core files or directories to add')
    args = parser.parse_args()

    if not Path('.pc').is_dir() or not os.environ.get('QUILT_PATCHES'):
        sys.exit('run this from the source tree with quilt variables set')

    header = _quilt('header')
    if not args.rev:
        match = _REV_LINE.search(header)
        if not match:
            sys.exit('no brave-core revision in the patch header, pass --rev')
        args.rev = match.group(1)
    rev = _git(args.brave_core, 'rev-parse', '--verify', f'{args.rev}^{{commit}}').decode().strip()

    tracked = {
        path[len(_PREFIX):]
        for path in _quilt('files').splitlines() if path.startswith(_PREFIX)
    }
    wanted = set(tracked)
    if args.paths:
        listed = _git(args.brave_core, 'ls-tree', '-r', '--name-only', rev, '--',
                      *args.paths).decode().splitlines()
        if not listed:
            sys.exit(f'nothing matches {args.paths} at {rev}')
        wanted.update(path for path in listed if not _SKIPPED.search(path))

    available = set(
        _git(args.brave_core, 'ls-tree', '-r', '--name-only', rev, '--',
             *sorted(wanted)).decode().splitlines())
    for path in sorted(wanted):
        dest = Path(_PREFIX + path)
        if path not in tracked:
            _quilt('add', str(dest))
        if path in available:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(_git(args.brave_core, 'show', f'{rev}:{path}'))
        else:
            print(f'removed upstream: {path}')
            dest.unlink(missing_ok=True)

    line = f'brave-core: {rev}'
    header = _REV_LINE.sub(line, header) if _REV_LINE.search(header) else \
        f'{header.rstrip()}\n\n{line}\n'.lstrip()
    _quilt('header', '-r', stdin=header)
    _quilt('refresh')
    print(f'vendored {len(wanted)} files from brave-core {rev}')


if __name__ == '__main__':
    main()
