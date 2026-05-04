#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.

# Copyright (c) 2019 The ungoogled-chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE.ungoogled_chromium file.
"""
Utility to ease the updating of platform patches against ungoogled-chromium's patches
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'utils'))
from _common import ENCODING, get_logger
from patches import merge_patches

sys.path.pop(0)

_SERIES = 'series'
_SERIES_ORIG = 'series.orig'
_SERIES_PREPEND = 'series.prepend'
_SERIES_MERGED = 'series.merged'


def merge_platform_patches(platform_patches_dir, prepend_patches_dir):
    '''
    Prepends prepend_patches_dir into platform_patches_dir

    Returns True if successful, False otherwise
    '''
    if not (platform_patches_dir / _SERIES).exists():
        get_logger().error('Unable to find platform series file: %s',
                           platform_patches_dir / _SERIES)
        return False

    # Make series.orig file
    shutil.copyfile(str(platform_patches_dir / _SERIES), str(platform_patches_dir / _SERIES_ORIG))

    # Make series.prepend
    shutil.copyfile(str(prepend_patches_dir / _SERIES), str(platform_patches_dir / _SERIES_PREPEND))

    # Merge patches
    merge_patches([prepend_patches_dir], platform_patches_dir, prepend=True)
    (platform_patches_dir / _SERIES).replace(platform_patches_dir / _SERIES_MERGED)

    return True


def _dir_empty(path):
    '''
    Returns True if the directory exists and is empty; False otherwise
    '''
    try:
        next(os.scandir(str(path)))
    except StopIteration:
        return True
    except FileNotFoundError:
        pass
    return False


def _rename_files_with_dirs(root_dir, source_dir, sorted_file_iter):
    '''
    Moves a list of sorted files back to their original location,
    removing empty directories along the way
    '''
    past_parent = None
    for partial_path in sorted_file_iter:
        complete_path = Path(root_dir, partial_path)
        complete_source_path = Path(source_dir, partial_path)
        try:
            complete_source_path.parent.mkdir(parents=True, exist_ok=True)
            complete_path.rename(complete_source_path)
        except FileNotFoundError:
            get_logger().warning('Could not move prepended patch: %s', complete_path)
        if past_parent != complete_path.parent:
            while past_parent and _dir_empty(past_parent):
                past_parent.rmdir()
                past_parent = past_parent.parent
            past_parent = complete_path.parent
    # Handle last path's directory
    while _dir_empty(complete_path.parent):
        complete_path.parent.rmdir()
        complete_path = complete_path.parent


def _series_path(series_line):
    return series_line.split(' #', maxsplit=1)[0]


def _parse_series_metadata(series_lines):
    paths = set()
    # patch path -> list of lines after patch path and before next patch path
    path_comments = {}
    # patch path -> inline comment for patch
    path_inline_comments = {}
    previous_path = None
    for partial_path in series_lines:
        if not partial_path or partial_path.startswith('#'):
            if previous_path not in path_comments:
                path_comments[previous_path] = []
            path_comments[previous_path].append(partial_path)
        else:
            previous_path = _series_path(partial_path)
            paths.add(previous_path)
            path_parts = partial_path.split(' #', maxsplit=1)
            if len(path_parts) == 2:
                path_inline_comments[previous_path] = path_parts[1]
    return paths, path_comments, path_inline_comments


def _restore_series_metadata(series, path_comments, path_inline_comments):
    series_index = 0
    while series_index < len(series):
        current_path = series[series_index]
        clean_path = _series_path(current_path)
        if clean_path in path_inline_comments:
            series[series_index] = clean_path + ' #' + path_inline_comments[clean_path]
        if clean_path in path_comments:
            series.insert(series_index + 1, '\n'.join(path_comments[clean_path]))
            series_index += 1
        series_index += 1


def unmerge_platform_patches(platform_patches_dir, prepend_patches_dir):
    '''
    Undo merge_platform_patches(), adding any new patches from series.merged as necessary

    Returns True if successful, False otherwise
    '''
    if not (platform_patches_dir / _SERIES_PREPEND).exists():
        get_logger().error('Unable to find series.prepend at: %s',
                           platform_patches_dir / _SERIES_PREPEND)
        return False
    prepend_series, prepend_path_comments, prepend_path_inline_comments = _parse_series_metadata(
        (platform_patches_dir / _SERIES_PREPEND).read_text(encoding=ENCODING).splitlines())

    # Determine positions of blank spaces in series.orig
    if not (platform_patches_dir / _SERIES_ORIG).exists():
        get_logger().error('Unable to find series.orig at: %s', platform_patches_dir / _SERIES_ORIG)
        return False
    orig_series_paths, path_comments, path_inline_comments = _parse_series_metadata(
        (platform_patches_dir / _SERIES_ORIG).read_text(encoding=ENCODING).splitlines())

    # Apply changes on series.merged into a modified version of series.orig
    if not (platform_patches_dir / _SERIES_MERGED).exists():
        get_logger().error('Unable to find series.merged at: %s',
                           platform_patches_dir / _SERIES_MERGED)
        return False
    merged_series = filter(len, (platform_patches_dir /
                                 _SERIES_MERGED).read_text(encoding=ENCODING).splitlines())
    generic_series = []
    new_series = []
    in_platform_series = False
    for current_path in merged_series:
        clean_path = _series_path(current_path)
        if clean_path in orig_series_paths:
            in_platform_series = True
        if clean_path in prepend_series or not in_platform_series:
            generic_series.append(current_path)
        else:
            new_series.append(current_path)

    # Move prepended files back to original location, preserving changes
    # including any new patches added before the platform patch block.
    _rename_files_with_dirs(
        platform_patches_dir, prepend_patches_dir,
        sorted(prepend_series.union(_series_path(patch_path) for patch_path in generic_series)))

    _restore_series_metadata(generic_series, prepend_path_comments, prepend_path_inline_comments)
    _restore_series_metadata(new_series, path_comments, path_inline_comments)

    # Write series file
    with (prepend_patches_dir / _SERIES).open('w', encoding=ENCODING) as series_file:
        series_file.write('\n'.join(generic_series))
        series_file.write('\n')
    with (platform_patches_dir / _SERIES).open('w', encoding=ENCODING) as series_file:
        series_file.write('\n'.join(new_series))
        series_file.write('\n')

    # All other operations are successful; remove merging intermediates
    (platform_patches_dir / _SERIES_MERGED).unlink()
    (platform_patches_dir / _SERIES_ORIG).unlink()
    (platform_patches_dir / _SERIES_PREPEND).unlink()

    return True


def main():
    """CLI Entrypoint"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',
                        choices=('merge', 'unmerge'),
                        help='Merge or unmerge ungoogled-chromium patches with platform patches')
    parser.add_argument('platform_patches',
                        type=Path,
                        help='The path to the platform patches in GNU Quilt format to merge into')
    args = parser.parse_args()

    repo_dir = Path(__file__).resolve().parent.parent

    success = False
    prepend_patches_dir = repo_dir / 'patches'
    if args.command == 'merge':
        success = merge_platform_patches(args.platform_patches, prepend_patches_dir)
    elif args.command == 'unmerge':
        success = unmerge_platform_patches(args.platform_patches, prepend_patches_dir)
    else:
        raise NotImplementedError(args.command)

    if success:
        return 0
    return 1


if __name__ == '__main__':
    sys.exit(main())
