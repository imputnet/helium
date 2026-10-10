#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Configure and materialize Helium's native adblock Rust workspace."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

_GN_ARG_PATTERN = re.compile(r'^\s*enable_native_adblock\s*=')


def _adblock_enabled():
    value = os.environ.get('ENABLE_ADBLOCK', 'false')
    if value in ('1', 'true'):
        return True
    if value in ('0', 'false'):
        return False
    raise ValueError('ENABLE_ADBLOCK must be 0, 1, false, or true')


def _set_gn_arg(args_gn, enabled):
    lines = args_gn.read_text(encoding='utf-8').splitlines()
    lines = [line for line in lines if not _GN_ARG_PATTERN.match(line)]
    lines.append(f'enable_native_adblock = {str(enabled).lower()}')
    args_gn.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def _copy_workspace_inputs(source, destination, chromium_workspace):
    (destination / '.cargo').mkdir(parents=True, exist_ok=True)
    (destination / 'src').mkdir(parents=True, exist_ok=True)

    for relative_path in ('Cargo.toml', 'Cargo.lock', 'gnrt_config.toml',
                          'src/lib.rs'):
        shutil.copyfile(source / relative_path, destination / relative_path)

    shutil.copyfile(chromium_workspace / '.cargo/config.toml',
                    destination / '.cargo/config.toml')
    shutil.copyfile(chromium_workspace / 'README.chromium.hbs',
                    destination / 'README.chromium.hbs')
    shutil.copyfile(chromium_workspace / 'BUILD.gn.hbs',
                    destination / 'BUILD.gn.hbs')


def _crate_epoch(version):
    major, minor, patch = version.split('.', 2)
    if major != '0':
        return f'v{major}'
    if minor != '0':
        return f'v0_{minor}'
    return f"v0_0_{patch.split('-', 1)[0]}"


def _cargo_metadata(src, workspace, environment):
    command = [
        sys.executable,
        str(src / 'tools/crates/run_cargo.py'),
        'metadata',
        '--locked',
        '--offline',
        '--format-version',
        '1',
        '--manifest-path',
        str(workspace / 'Cargo.toml'),
    ]
    result = subprocess.run(command,
                            cwd=workspace,
                            env=environment,
                            check=True,
                            capture_output=True,
                            text=True)
    return json.loads(result.stdout)


def _local_packages(metadata):
    workspace_members = set(metadata['workspace_members'])
    return [package for package in metadata['packages']
            if package['source'] is None and
            package['id'] not in workspace_members]


def _generate_forwarders(src, metadata):
    for package in _local_packages(metadata):
        name = package['name']
        version = package['version']
        target_name = name.replace('-', '_')
        epoch = _crate_epoch(version)
        upstream = src / 'third_party/rust' / target_name / epoch
        destination = src / 'third_party/rust/helium' / target_name / epoch
        if not (upstream / 'BUILD.gn').is_file():
            raise FileNotFoundError(
                f'missing Chromium GN target for {target_name} {epoch}')

        destination.mkdir(parents=True, exist_ok=True)
        (destination / 'BUILD.gn').write_text(
            '# Copyright 2026 The Helium Authors\n'
            '# Use of this source code is governed by a BSD-style license that can be\n'
            '# found in the LICENSE file.\n\n'
            'group("lib") {\n'
            f'  public_deps = [ "//third_party/rust/{target_name}/{epoch}:lib" ]\n'
            '}\n',
            encoding='utf-8')
        readme = upstream / 'README.chromium'
        if readme.is_file():
            shutil.copyfile(readme, destination / 'README.chromium')


def _write_engine_version(workspace, metadata):
    versions = {package['version'] for package in metadata['packages']
                if package['name'] == 'adblock'}
    if len(versions) != 1:
        raise ValueError('cargo metadata did not resolve exactly one adblock crate')
    version = versions.pop()
    (workspace / 'adblock_engine_version.h').write_text(
        '// Copyright 2026 The Helium Authors\n'
        '// Use of this source code is governed by a BSD-style license that can be\n'
        '// found in the LICENSE file.\n\n'
        '#ifndef THIRD_PARTY_RUST_HELIUM_CHROMIUM_CRATES_IO_ADBLOCK_ENGINE_VERSION_H_\n'
        '#define THIRD_PARTY_RUST_HELIUM_CHROMIUM_CRATES_IO_ADBLOCK_ENGINE_VERSION_H_\n\n'
        'namespace helium_adblock {\n\n'
        f'inline constexpr char kEngineVersion[] = "adblock-{version}";\n\n'
        '}  // namespace helium_adblock\n\n'
        '#endif  // THIRD_PARTY_RUST_HELIUM_CHROMIUM_CRATES_IO_ADBLOCK_ENGINE_VERSION_H_\n',
        encoding='utf-8')


def _materialize_workspace(src, gn_dir):
    workspace_source = src / 'components/helium_adblock/rs/crates'
    workspace = src / 'third_party/rust/helium/chromium_crates_io'
    chromium_workspace = src / 'third_party/rust/chromium_crates_io'
    _copy_workspace_inputs(workspace_source, workspace, chromium_workspace)

    environment = os.environ.copy()
    if gn_dir:
        environment['PATH'] = (str(gn_dir.resolve()) + os.pathsep +
                               environment.get('PATH', ''))

    command = [sys.executable, 'tools/crates/run_gnrt.py',
               '--third-party-workspace', 'helium']
    subprocess.run(command + ['vendor'], cwd=src, env=environment, check=True)
    metadata = _cargo_metadata(src, workspace, environment)
    subprocess.run(command + ['gen'], cwd=src, env=environment, check=True)
    _generate_forwarders(src, metadata)
    _write_engine_version(workspace, metadata)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('chromium_src', type=Path)
    parser.add_argument('args_gn', type=Path)
    parser.add_argument('--gn-dir', type=Path)
    args = parser.parse_args()

    enabled = _adblock_enabled()
    _set_gn_arg(args.args_gn.resolve(), enabled)
    if enabled:
        _materialize_workspace(args.chromium_src.resolve(), args.gn_dir)


if __name__ == '__main__':
    try:
        main()
    except ValueError as exc:
        print(f'error: {exc}', file=sys.stderr)
        sys.exit(1)
