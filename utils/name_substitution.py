#!/usr/bin/env python3

# Copyright 2025 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Script to replace instances of Chrome/Chromium with Helium"""

from concurrent.futures import ProcessPoolExecutor
from tarfile import TarInfo
from pathlib import Path
import argparse
import tarfile
import os
import io

import name_substitution_utils as util

IGNORE_DIRS = ['.pc', 'chromeos', 'remoting', 'ash', 'android', 'ios']


def replacement_sanity():
    """Sanity check to ensure replacement regexes are working as intended"""
    before_after = [
        ('Chrome Root Program', 'Chrome Root Program'),
        ('Chrome Web Store', 'Chrome Web Store'),
        ('Chromium Web Store', 'Chromium Web Store'),
        ('Chrome Remote Desktop', 'Chrome Remote Desktop'),
        ('Google Chrome', 'Helium'),
        ('Chrome Google Chrome Chrome Chromium', 'Helium Helium Helium Helium'),
        ('Chrome', 'Helium'),
        ('Chromium', 'Helium'),
    ]

    for source, expected in before_after:
        assert util.replace_text(source) == expected


def parse_args():
    """CLI argument parsing logic"""
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--sub', action='store_true')
    group.add_argument('--unsub', action='store_true')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--backup-path', metavar='<tarball-path>', type=Path)
    group.add_argument('--dry-run', action='store_true')
    parser.add_argument('-t', metavar='source_tree', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=os.cpu_count())

    args = parser.parse_args()

    if args.unsub and not args.backup_path:
        raise ValueError("backup_path is missing, but unsub was specified")

    return args


def get_substitutable_files(tree, exts):
    """
    Finds all candidates for substitution, which have one of the
    desired extensions - typically string files (.grd*),
    or localization files (.xtb).
    """
    out = tree / 'out'

    for root, _, files in os.walk(tree):
        root = Path(root)
        if out in root.parents:
            continue

        should_ignore = False
        for dir_name in IGNORE_DIRS:
            if dir_name in root.parts:
                should_ignore = True
                break

        if should_ignore:
            continue

        for filename in files:
            if filename.startswith('.'):
                continue
            ext = filename.split('.')[-1].lower()
            if ext not in exts:
                continue
            yield root / filename


def substitute_file(args):
    """
    Replaces strings in a particular file, and returns
    ((arcname, original_content), fp_map) if file was modified and needs backup,
    (None, fp_map) if file was modified,
    otherwise None.
    """
    path, tree, save_original, dry_run = args
    arcname = str(path.relative_to(tree))

    with open(path, 'r', encoding='utf-8') as file:
        text = file.read()

    replaced, fp_map = util.replace_grit_tree(text)
    if not fp_map:
        return None

    print(f"Replaced strings in {arcname}")
    if not dry_run:
        with open(path, 'w', encoding='utf-8') as file:
            file.write(replaced)

    return ((arcname, text) if save_original else None, fp_map)


def do_unsubstitution(tree, tarpath):
    """Reverts name substitutions from the backup tarball"""
    with tarfile.open(str(tarpath), 'r:gz') as tar:
        tar.extractall(path=tree, filter='fully_trusted')
    tarpath.unlink()


def maybe_make_tarball(tar_path, modified_files):
    """
    Creates a backup tarball if requested by arguments.
    """
    if tar_path is None:
        return

    with tarfile.open(str(tar_path), 'w:gz') as tar:
        for arcname, content in modified_files:
            content = content.encode('utf-8')
            tarinfo = TarInfo(name=arcname)
            tarinfo.size = len(content)
            tar.addfile(tarinfo, io.BytesIO(content))


def do_substitution(tree, tarpath, workers, dry_run):
    """Performs name substitutions on all candidate files"""
    files = list(get_substitutable_files(tree, ['grd', 'grdp', 'xtb']))
    print(f"Found {len(files)} files to process")

    with ProcessPoolExecutor(max_workers=workers) as executor:
        save_original = tarpath is not None
        file_args = [(path, tree, save_original, dry_run) for path in files]
        results = executor.map(substitute_file, file_args)
        modified_files = [r for r in results if r is not None]

    maybe_make_tarball(tarpath, modified_files)
    print(f"Modified {len(modified_files)} files")


def main():
    """CLI entrypoint"""
    replacement_sanity()
    args = parse_args()

    if not (args.t / "OWNERS").exists():
        raise ValueError("wrong src directory")

    util.add_grit_to_path(args.t)

    if args.sub:
        if args.backup_path is not None and args.backup_path.exists():
            raise FileExistsError("unsub tarball already exists, aborting")
        do_substitution(args.t, args.backup_path, args.workers, args.dry_run)
    elif args.unsub and args.backup_path and not args.dry_run:
        do_unsubstitution(args.t, args.backup_path)


if __name__ == '__main__':
    main()
