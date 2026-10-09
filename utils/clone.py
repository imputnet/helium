#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Copyright 2026 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.

# Copyright (c) 2023 The ungoogled-chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE.ungoogled_chromium file.
"""Clone fresh Chromium sources and prepare their dependencies with gclient."""

import os
import re
import sys
from argparse import ArgumentParser
from pathlib import Path
from subprocess import run

from _common import ENCODING, add_common_params, get_chromium_version, get_logger


def checkout(url, revision, destination, environment):
    """Fetch a pinned revision, retaining the parent needed by lastchange."""
    if not (destination / '.git').exists():
        destination.mkdir(parents=True, exist_ok=True)
        run(['git', 'init', '-q', str(destination)], env=environment, check=True)
        run(['git', '-C', str(destination), 'remote', 'add', 'origin', url],
            env=environment,
            check=True)
    run(['git', '-C', str(destination), 'fetch', '--depth=2', 'origin', revision],
        env=environment,
        check=True)
    run(['git', '-C',
         str(destination), 'checkout', '--detach', '--force', 'FETCH_HEAD'],
        env=environment,
        check=True)


def clone(args):
    """Sync pinned sources, binary dependencies, and upstream hooks."""
    output = args.output.resolve()
    root = output.parent
    depot = root / 'depot_tools'
    environment = os.environ.copy()
    environment.update({
        'PATH': str(depot) + os.pathsep + environment.get('PATH', ''),
        'DEPOT_TOOLS_UPDATE': '0',
        'PYTHONDONTWRITEBYTECODE': '1',
    })
    if sys.platform == 'win32':
        environment['DEPOT_TOOLS_WIN_TOOLCHAIN'] = '0'

    get_logger().info('cloning chromium %s', get_chromium_version())
    checkout('https://chromium.googlesource.com/chromium/src',
             'refs/tags/' + get_chromium_version(), output, environment)
    revision = run(['git', '-C', str(output), 'rev-parse', 'HEAD'],
                   env=environment,
                   check=True,
                   capture_output=True,
                   text=True).stdout.strip()
    depot_commit = args.dt_commit or re.search(
        r"depot_tools\.git'\s*\+\s*'@'\s*\+\s*'([^']+)',",
        (output / 'DEPS').read_text(encoding=ENCODING)).group(1)
    checkout('https://chromium.googlesource.com/chromium/tools/depot_tools', depot_commit, depot,
             environment)

    config_file = root / '.gclient'
    if args.custom_config:
        config_file.write_text(args.custom_config.read_text(encoding=ENCODING).replace(
            'UC_OUT', 'src'),
                               encoding=ENCODING)
    else:
        target_os = 'win' if args.pgo.startswith('win') else args.pgo.split('-')[0]
        targets = ['x64', 'arm64']
        if args.pgo == 'win32':
            targets.append('x86')
        config = {
            'solutions': [{
                'name': 'src',
                'url': 'https://chromium.googlesource.com/chromium/src',
                'managed': True,
                'custom_vars': {
                    'checkout_configuration': 'small',
                    'checkout_pgo_profiles': True,
                    'checkout_android': False,
                    'checkout_ios': False,
                    'checkout_chromeos': False,
                    'checkout_fuchsia': False,
                },
            }],
            'target_os': [target_os],
            'target_os_only': True,
            'target_cpu': targets,
            'target_cpu_only': True,
            'cache_dir': None,
        }
        config_file.write_text(''.join(f'{key} = {value!r}\n' for key, value in config.items()),
                               encoding=ENCODING)
    environment['GCLIENT_FILE'] = str(config_file)
    gclient = depot / ('gclient.bat' if sys.platform == 'win32' else 'gclient')
    command = ['cmd.exe', '/d', '/c', str(gclient)] if sys.platform == 'win32' else [str(gclient)]
    run(command + [
        'sync', '--no-history', '--force', '--reset', '--delete_unversioned_trees', '--revision',
        'src@' + revision
    ],
        cwd=root,
        env=environment,
        check=True)
    get_logger().info('source cloning complete')


def main():
    """CLI entrypoint."""
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-o',
                        '--output',
                        type=Path,
                        default=Path('src'),
                        help='Empty source directory named src. Default: %(default)s')
    parser.add_argument('-c',
                        '--custom-config',
                        type=Path,
                        help='Replacement gclient configuration.')
    parser.add_argument('-p',
                        '--pgo',
                        default={
                            'linux': 'linux',
                            'darwin': 'mac',
                            'win32': 'win64'
                        }[sys.platform],
                        choices=('linux', 'mac', 'mac-arm', 'win32', 'win64', 'win-arm64'),
                        help='Target platform for dependencies and PGO profiles.')
    parser.add_argument('--dt-commit', help='Override the depot_tools revision from DEPS.')
    add_common_params(parser)
    args = parser.parse_args()
    if args.output.resolve().name != 'src':
        parser.error('the output directory must be named src for gclient hooks')
    if args.output.exists() and (not args.output.is_dir() or any(args.output.iterdir())):
        parser.error('source directory is not empty; move it aside or use a fresh src directory')
    clone(args)


if __name__ == '__main__':
    main()
