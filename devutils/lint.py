#!/usr/bin/env python3

# Copyright 2025 The Kaguya Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Script to run sanity checks against the Kaguya patchset."""

import sys
import inspect
import argparse
from pathlib import Path

import _lint_tests


def parse_args():
    """Parses the CLI arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tree', help='root of the source tree to check')
    return parser.parse_args()


def main():
    """CLI entrypoint for executing tests"""
    args = parse_args()
    root_dir = (Path(__file__).parent / "..").resolve()

    if args.tree:
        root_dir = Path(args.tree).resolve()

    _lint_tests._init(root_dir) # pylint: disable=protected-access

    for name, func in inspect.getmembers(_lint_tests, inspect.isfunction):
        if name.startswith("_"):
            continue

        try:
            func()
            print(f"[OK] {name}")
        except Exception:
            print(f"[ERR] {name}:", file=sys.stderr)
            raise


if __name__ == '__main__':
    main()
