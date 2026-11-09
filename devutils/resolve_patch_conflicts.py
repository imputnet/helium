#!/usr/bin/env python3
# Copyright 2026 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""
Resolve trivial Git conflicts in quilt patch files.

Patches should be pushed and refreshed with quilt afterwards.
"""

import argparse
import subprocess
import sys


def _git(*args, **kwargs):
    return subprocess.run(['git', *args], check=True, stdout=subprocess.PIPE, **kwargs).stdout


def _unmerged_stages():
    """Returns {path: {stage: blob}} for all unmerged paths"""
    paths = {}
    for entry in _git('ls-files', '-u', '-z').split(b'\0'):
        if not entry:
            continue
        info, path = entry.split(b'\t', 1)
        _, blob, stage = info.split(b' ')
        paths.setdefault(path.decode(), {})[int(stage)] = blob.decode()
    return paths


def _changes(blob):
    """
    Returns the content of a patch without hunk line numbers.
    Context lines are kept, so that edits that moved elsewhere
    in the same file are not mistaken for offset changes.
    """
    if blob is None:
        return None
    content = _git('cat-file', 'blob', blob)
    return [b'@@' if line.startswith(b'@@') else line for line in content.splitlines()]


def _resolve(path, stages):
    """
    Returns ('take', blob), ('delete', None) or (None, reason)
    for a set of conflicting stages (1 = base, 2 = ours, 3 = theirs).
    """
    base, ours, theirs = (stages.get(i) for i in (1, 2, 3))

    if ours is None or theirs is None:
        # Added on one side only, e.g. moved there by rename detection.
        if base is None:
            return None, 'added on one side only'
        # The file is either obsolete upstream, or was replaced by our own
        # implementation. Either way, it should go.
        return 'delete', None

    if not path.endswith('.patch'):
        return None, 'not a patch'

    base_c, ours_c, theirs_c = map(_changes, (base, ours, theirs))

    if theirs_c in (base_c, ours_c):
        return 'take', ours
    if ours_c == base_c:
        return 'take', theirs
    return None, 'changed on both sides'


def main():
    """CLI entrypoint"""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-n',
                        '--dry-run',
                        action='store_true',
                        help='Only print what would be done.')
    parser.add_argument('paths',
                        nargs='*',
                        help='Conflicted paths to resolve. Defaults to all unmerged paths.')
    args = parser.parse_args()

    unmerged = _unmerged_stages()
    paths = args.paths or sorted(unmerged)
    unresolved = False

    for path in paths:
        if path not in unmerged:
            print(f'{path}: not unmerged, skipping', file=sys.stderr)
            continue

        action, arg = _resolve(path, unmerged[path])
        if action is None:
            print(f'{path}: unresolved ({arg})', file=sys.stderr)
            unresolved = True
            continue

        print(f'{path}: {"deleted" if action == "delete" else "resolved"}')
        if args.dry_run:
            continue
        if action == 'delete':
            _git('rm', '--quiet', '--', path)
        else:
            with open(path, 'wb') as file:
                file.write(_git('cat-file', 'blob', arg))
            _git('add', '--', path)

    if unresolved:
        sys.exit(1)


if __name__ == '__main__':
    main()
