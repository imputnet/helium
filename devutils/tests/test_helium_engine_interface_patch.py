# -*- coding: UTF-8 -*-

# Copyright 2026 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Tests for patches/helium/core/sync/engine-interface.patch

This patch is supposed to introduce three new files
(components/sync/engine/custom_sync_backend.h,
components/sync/service/helium_sync_backend.h and
components/sync/service/helium_sync_backend.cc) and wire a fallback to the
Helium-provided sync backend into six existing sync engine/service files.
"""

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'third_party'))
import unidiff
from unidiff.errors import UnidiffParseError

sys.path.pop(0)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'utils'))
from _common import ENCODING

sys.path.pop(0)

_ROOT_DIR = Path(__file__).resolve().parent.parent.parent
_PATCH_PATH = _ROOT_DIR / 'patches' / 'helium' / 'core' / 'sync' / 'engine-interface.patch'
_HELIUM_BACKEND_HEADER_PATH = (_ROOT_DIR / 'components' / 'sync' / 'service' /
                               'helium_sync_backend.h')
_HELIUM_BACKEND_IMPL_PATH = (_ROOT_DIR / 'components' / 'sync' / 'service' /
                             'helium_sync_backend.cc')

# A single leading unified-diff marker (' ', '+', or '-') immediately followed by another
# "--- ", "+++ ", or "@@ -N" sequence indicates a nested/leftover diff-of-diffs marker
# that should never appear in a properly generated patch file.
_NESTED_DIFF_MARKER_RE = re.compile(r'^[ +\-](?:--- |\+\+\+ |@@ -\d)', re.MULTILINE)

_EXPECTED_MODIFIED_FILES = {
    'components/sync/engine/sync_engine.cc',
    'components/sync/engine/sync_engine.h',
    'components/sync/engine/sync_manager.cc',
    'components/sync/engine/sync_manager.h',
    'components/sync/engine/sync_manager_impl.cc',
    'components/sync/service/glue/sync_engine_backend.cc',
}

_EXPECTED_ADDED_FILES = {
    'components/sync/engine/custom_sync_backend.h',
    'components/sync/service/helium_sync_backend.h',
    'components/sync/service/helium_sync_backend.cc',
}


def _read_patch_text():
    return _PATCH_PATH.read_text(encoding=ENCODING)


_FIRST_ADDED_FILE_HEADER_RE = re.compile(
    r'\A--- /dev/null\n\+\+\+ b/(?P<path>\S+)\n@@ -0,0 \+1,(?P<count>\d+) @@\n')


def _added_files_preamble():
    """Returns exactly the "add new file" hunk for custom_sync_backend.h.

    This is extracted using only the hunk's own (well-formed) header and
    declared line count, so it is independently parseable regardless of
    whatever content follows it later in the file.
    """
    text = _read_patch_text()
    match = _FIRST_ADDED_FILE_HEADER_RE.match(text)
    assert match, 'Patch does not start with a well-formed "add new file" diff header'
    count = int(match.group('count'))
    remainder_lines = text[match.end():].splitlines(keepends=True)
    content_lines = remainder_lines[:count]
    assert len(content_lines) == count, 'Patch is truncated before the declared hunk length'
    return text[:match.end()] + ''.join(content_lines)


def _custom_sync_backend_patched_file():
    patch_set = unidiff.PatchSet(_added_files_preamble())
    assert len(patch_set) == 1
    return patch_set[0]


def _added_lines_text(patched_file):
    assert len(patched_file) == 1
    return '\n'.join(line.value.rstrip('\n') for line in patched_file[0])


# -----------------------------------------------------------------------------------
# Basic file sanity
# -----------------------------------------------------------------------------------


def test_patch_file_exists():
    assert _PATCH_PATH.is_file()


def test_patch_file_ends_with_trailing_newline():
    # devutils/validate_patches.py's _load_all_patches() treats a patch file that does
    # not end with a newline as a validation failure.
    assert _read_patch_text().endswith('\n')


# -----------------------------------------------------------------------------------
# components/sync/engine/custom_sync_backend.h addition.
#
# This is the one purely-added-file hunk in the patch whose diff syntax remains
# well-formed on its own, so it can be parsed and checked in isolation.
# -----------------------------------------------------------------------------------


def test_custom_sync_backend_addition_is_well_formed():
    patched_file = _custom_sync_backend_patched_file()
    assert patched_file.path == 'components/sync/engine/custom_sync_backend.h'
    assert patched_file.is_added_file
    assert len(patched_file) == 1
    hunk = patched_file[0]
    assert hunk.source_start == 0
    assert hunk.source_length == 0
    assert hunk.target_start == 1
    assert hunk.target_length == 33
    assert len(hunk) == 33


def test_custom_sync_backend_header_guard_and_namespace():
    text = _added_lines_text(_custom_sync_backend_patched_file())
    assert '#ifndef COMPONENTS_SYNC_ENGINE_CUSTOM_SYNC_BACKEND_H_' in text
    assert '#define COMPONENTS_SYNC_ENGINE_CUSTOM_SYNC_BACKEND_H_' in text
    assert '#endif  // COMPONENTS_SYNC_ENGINE_CUSTOM_SYNC_BACKEND_H_' in text
    assert 'namespace syncer {' in text
    assert text.count('}  // namespace syncer') == 1


def test_custom_sync_backend_declares_expected_interface():
    text = _added_lines_text(_custom_sync_backend_patched_file())
    assert 'class CancelationSignal;' in text
    assert 'class ServerConnectionManager;' in text
    assert 'class CustomSyncBackend {' in text
    assert 'CustomSyncBackend() = default;' in text
    assert 'CustomSyncBackend(const CustomSyncBackend&) = delete;' in text
    assert 'CustomSyncBackend& operator=(const CustomSyncBackend&) = delete;' in text
    assert 'virtual ~CustomSyncBackend() = default;' in text
    assert 'virtual std::unique_ptr<ServerConnectionManager> CreateConnectionManager(' in text
    assert 'CancelationSignal* cancelation_signal) = 0;' in text
    assert 'virtual std::string GetDebugName() const = 0;' in text


def test_custom_sync_backend_includes_required_headers():
    text = _added_lines_text(_custom_sync_backend_patched_file())
    assert '#include <memory>' in text
    assert '#include <string>' in text


# -----------------------------------------------------------------------------------
# Cross-check against the tracked Helium shim source files
# (components/sync/service/helium_sync_backend.{h,cc}), which mirror what the
# corresponding (currently corrupted, see below) hunks of the patch are meant to add.
# -----------------------------------------------------------------------------------


def test_tracked_helium_sync_backend_header_declares_factory_function():
    text = _HELIUM_BACKEND_HEADER_PATH.read_text(encoding=ENCODING)
    assert '#include "components/sync/engine/custom_sync_backend.h"' in text
    assert 'std::unique_ptr<CustomSyncBackend> CreateHeliumCustomSyncBackend();' in text
    assert 'namespace syncer {' in text


def test_tracked_helium_sync_backend_impl_default_is_noop():
    text = _HELIUM_BACKEND_IMPL_PATH.read_text(encoding=ENCODING)
    assert '#include "components/sync/service/helium_sync_backend.h"' in text
    assert '#include "components/sync/engine/custom_sync_backend.h"' in text
    assert 'std::unique_ptr<CustomSyncBackend> CreateHeliumCustomSyncBackend() {' in text
    assert 'return nullptr;' in text


# -----------------------------------------------------------------------------------
# Whole-file integrity regression tests.
#
# The patch is meant to be a single, self-contained unified diff that adds three new
# files and wires up six existing engine/service files (see _EXPECTED_ADDED_FILES /
# _EXPECTED_MODIFIED_FILES above). The tests below currently fail because the
# committed patch contains leftover, un-collapsed diff-of-diffs markers past the
# custom_sync_backend.h addition (e.g. " --- a/...", "-@@ ... @@", "+@@ ... @@"),
# which makes it unparsable/unusable by patch(1), git apply, and
# devutils/validate_patches.py alike.
# -----------------------------------------------------------------------------------


def test_patch_has_no_leftover_meta_diff_markers():
    """The patch must not contain nested/duplicated diff markers.

    A correctly generated patch never has a content line whose leading
    " "/"+"/"-" prefix is immediately followed by another "--- ", "+++ ", or
    "@@ -N" sequence; that pattern only appears when a diff-of-diffs was pasted
    into the file without being collapsed into final file content.
    """
    matches = _NESTED_DIFF_MARKER_RE.findall(_read_patch_text())
    assert not matches, (
        f'Found {len(matches)} leftover meta-diff marker(s) in the patch file: {matches}. '
        'The patch content was not fully resolved from a diff-of-diffs.')


def test_full_patch_file_is_a_valid_unified_diff():
    try:
        unidiff.PatchSet.from_filename(str(_PATCH_PATH), encoding=ENCODING)
    except UnidiffParseError as exc:
        pytest.fail(
            f'patches/helium/core/sync/engine-interface.patch is not a valid unified '
            f'diff and cannot be applied: {exc}')


def test_patch_declares_all_expected_added_and_modified_files():
    patch_set = unidiff.PatchSet.from_filename(str(_PATCH_PATH), encoding=ENCODING)
    added_paths = {patched_file.path for patched_file in patch_set if patched_file.is_added_file}
    modified_paths = {
        patched_file.path
        for patched_file in patch_set
        if not patched_file.is_added_file
    }
    assert added_paths == _EXPECTED_ADDED_FILES
    assert _EXPECTED_MODIFIED_FILES <= modified_paths


def test_sync_engine_backend_fallback_wiring_text_present():
    """Sanity check that the intended fallback-to-Helium-shim wiring exists somewhere
    in the patch text, independent of whether it is nested inside correctly-formed
    diff syntax (see test_full_patch_file_is_a_valid_unified_diff)."""
    text = _read_patch_text()
    assert '#include "components/sync/service/helium_sync_backend.h"' in text
    assert 'if (params.custom_sync_backend) {' in text
    assert 'args.custom_sync_backend = std::move(params.custom_sync_backend);' in text
    assert 'args.custom_sync_backend = syncer::CreateHeliumCustomSyncBackend();' in text
