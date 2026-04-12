# Copyright 2026 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""
String extraction from Helium patches for translation.
"""

import subprocess
import json
from pathlib import Path

from third_party import unidiff

import utils.name_substitution_utils as namesub # pylint: disable=wrong-import-order

PLATFORMS = ("windows", "macos", "linux")
REPO_URL = "https://github.com/imputnet/helium-{platform}.git"


def prep_platform_repos(platforms_dir):
    """Clone and update platform repos into the given directory."""
    platforms_dir.mkdir(parents=True, exist_ok=True)

    for platform in PLATFORMS:
        dest = platforms_dir / platform
        if not dest.is_dir():
            subprocess.run(
                ["git", "clone", REPO_URL.format(platform=platform),
                 str(dest)],
                check=True,
            )
        subprocess.check_call(["git", "-C", str(dest), "checkout", "main"])
        subprocess.check_call(["git", "-C", str(dest), "pull"])


def get_patch_paths(repo_root, platforms_dir):
    """
    Generate patch file paths from all series files (main repo + platforms).
    """
    series_files = [repo_root / "patches" / "series"] + \
        [platforms_dir / platform / "patches" / "series" for platform in PLATFORMS]

    for series_file in series_files:
        patches_dir = series_file.parent
        for line in series_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            yield str(patches_dir / line.split()[0])


def get_relevant_patches(repo_root, platforms_dir):
    """Generate patched hunks from patches that touch .grd or .grdp files."""
    for path in get_patch_paths(repo_root, platforms_dir):
        patch_set = unidiff.PatchSet.from_filename(path)
        for file in patch_set:
            if Path(file.path).suffix in ['.grd', '.grdp']:
                yield file


def extract_strings_from_hunk(hunk):
    """
    Parse a diff hunk and generate (name, desc, message)
    for added GRD message elements.

    What we want:
    - any completely new unit
    - any unit where the string or metadata was changed
    What we don't want:
    - untouched (ergo already translated) units
    - broken chunks of untouched, pre-existing units
    - units that were added in a different patch (avoiding duplication)
    """
    name, message, desc = None, '', None
    meta_acc = ''
    had_any_additive = False

    for line in str(hunk).split('\n'):
        is_additive = line.startswith('+')
        is_subtractive = line.startswith('-')
        line = line.lstrip('+-').strip()

        if line.startswith('<message') or meta_acc:
            meta_acc += line
        elif line.startswith('</message>'):
            if name and message and had_any_additive:
                yield name, desc, message
            name, message, desc = None, '', None
            had_any_additive = False
        elif name and not is_subtractive:
            message += line

        if meta_acc and line.endswith('>'):
            name = meta_acc.split('name="')[1].split('"')[0]
            desc = meta_acc.split('desc="')[1].split('"')[0]
            meta_acc = ''

        had_any_additive |= bool(name) and is_additive


def extract_strings(repo_root, platforms_dir):
    """Generate strings to be translated for all grit strings in patches."""
    for patch in get_relevant_patches(repo_root, platforms_dir):
        for hunk in patch:
            for name, desc, message in extract_strings_from_hunk(hunk):
                context = namesub.replace_text(desc)[0]
                message = namesub.replace_text(message)[0]

                yield {
                    'name': name,
                    'source': patch.path,
                    'context': context,
                    'message': message,
                }


def run(args, repo_root):
    """Generate the base source strings JSON from patches."""
    prep_platform_repos(args.platforms_dir)
    namesub.add_grit_to_path(args.tree)

    with open(args.output, 'w', encoding='utf-8') as out:
        data = json.dumps(
            list(extract_strings(repo_root, args.platforms_dir)),
            indent=2,
            ensure_ascii=False,
        )
        out.write(data + '\n')
