#!/usr/bin/env python3

# Copyright 2025 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""
Replaces resources (such as icons) with Helium branding.
"""

import os
import shutil
import sys


def copy_resources(resource_list, resource_dir, chromium_dir):
    """
    Handles copying resources from the source tree into the build
    tree based on a resources list.
    """
    with open(resource_list, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            line_parts = line.split()

            if len(line_parts) != 2:
                raise ValueError(f"Line {line_number} in the resource file is invalid.")

            source = os.path.join(resource_dir, line_parts[0])
            dest = os.path.join(chromium_dir, line_parts[1])

            shutil.copyfile(source, dest)
            print(f"Copied {line_parts[0]} to {line_parts[1]}")


def main():
    """CLI entrypoint"""
    if len(sys.argv) != 4:
        print(
            "Usage: python3 replace_resources.py <helium_resources.txt> " \
            "<resources_dir> <chromium_src_dir>"
        )
        sys.exit(1)

    resource_list = sys.argv[1]
    resource_dir = sys.argv[2]
    chromium_dir = sys.argv[3]

    copy_resources(resource_list, resource_dir, chromium_dir)


if __name__ == "__main__":
    main()
