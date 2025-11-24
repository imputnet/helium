# pylint: disable=missing-function-docstring,invalid-name,global-statement,missing-module-docstring
# Copyright 2025 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.

from third_party import unidiff

LICENSE_HEADER_IGNORES = ["html", "license", "readme"]

patches_dir = None
series = None


def _read_text(path):
    with open(patches_dir / path, "r", encoding="utf-8") as f:
        return filter(str, f.read().splitlines())


def _read_patch(path):
    return unidiff.PatchSet('\n'.join(_read_text(path)))


def _init(root):
    global patches_dir
    global series
    patches_dir = root / "patches"
    series = set(_read_text("series"))


def a_all_patches_in_series_exist():
    for patch in series:
        assert (patches_dir / patch).is_file(), \
               f"{patch} is in series, but does not exist in the source tree"


def a_all_patches_in_tree_are_in_series():
    for patch in patches_dir.rglob('*'):
        if not patch.is_file() or patch == patches_dir / "series":
            continue

        assert str(patch.relative_to(patches_dir)) in series, \
               f"{patch} exists in source tree, but is not included in the series"


def b_all_patches_have_meaningful_contents():
    for patch in series:
        assert any(l.startswith('+++ ') for l in _read_text(patch)), \
               f"{patch} does not have any meaningful content"


def b_all_patches_have_no_trailing_whitespace():
    for patch in series:
        for i, line in enumerate(_read_text(patch)):
            if not line.startswith('+ '):
                continue

            assert not line.endswith(' '), \
                   f"{patch} contains trailing whitespace on line {i + 1}"


def c_all_new_files_have_license_header():
    for patch in series:
        if 'helium' not in patch:
            continue

        added_files = filter(lambda f: f.is_added_file, _read_patch(patch))

        for file in added_files:
            if any(p in file.path.lower() for p in LICENSE_HEADER_IGNORES):
                continue

            assert any('terms of the GPL-3.0 license' in str(hunk) for hunk in file), \
                   f"File {file.path} was added in {patch}, but contains no Helium license header"


def c_all_new_headers_have_correct_guard():
    for patch in series:
        if 'helium' not in patch:
            continue

        added_files = filter(lambda f: f.is_added_file and f.path.endswith('.h'),
                             _read_patch(patch))

        for file in added_files:
            expected_macro_name = file.path.upper() \
                                  .replace('.', '_') \
                                  .replace('/', '_') + '_'

            assert len(file) == 1

            expected = {
                "ifndef": f'#ifndef {expected_macro_name}',
                "define": f'#define {expected_macro_name}'
            }

            found = {
                "ifndef": None,
                "define": None,
            }

            for _line in file[0]:
                line = str(_line)

                if '#ifndef' in line:
                    assert found["define"] is None
                    assert found["ifndef"] is None
                    found["ifndef"] = line
                elif '#define' in line:
                    assert found["ifndef"] is not None
                    assert found["define"] is None
                    found["define"] = line

            for macro_type, value in found.items():
                value_print = (value or '(none)').rstrip()
                assert value == f"+{expected[macro_type]}\n", \
                       f"Patch {patch} has unexpected {macro_type} in {file.path}:" \
                       f"{value_print}, expecting: {expected[macro_type]}"


def d_no_whitespace_only_changes():
    for patch in series:
        if 'helium' not in patch:
            continue

        for file in _read_patch(patch):
            for hunk in file:
                seen_nonws = False
                for line in hunk:
                    line = str(line)

                    if line.startswith('+') or line.startswith('-'):
                        seen_nonws = seen_nonws or len(line.rstrip()) > 1

                assert seen_nonws, \
                    f"Patch {patch} contains hunk consisting of "\
                    f"only whitespace characters in {file.path}: {hunk}"
