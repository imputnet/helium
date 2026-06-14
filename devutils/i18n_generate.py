# Copyright 2026 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""
String extraction from Helium patches for translation.
"""

import subprocess
import json
import sys
import re
from pathlib import Path

from third_party import unidiff

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'utils'))

from downloads import DownloadInfo # pylint: disable=wrong-import-order
import utils.name_substitution_utils as namesub # pylint: disable=wrong-import-order

PLATFORMS = ("windows", "macos", "linux")
REPO_URL = "https://github.com/imputnet/helium-{repo}.git"
ROOT_DIR = Path(__file__).resolve().parent.parent
ONBOARDING_VERSION = DownloadInfo([ROOT_DIR / "deps.ini"])['onboarding'].version


def get_xml_attr(text, attr):
    """Extract an XML attribute from an opening tag."""
    match = re.search(rf'{attr}="([^"]*)"', text)
    return match.group(1) if match else None


def prep_platform_repos(platforms_dir):
    """Clone and update platform repos into the given directory."""
    platforms_dir.mkdir(parents=True, exist_ok=True)

    for repo in list(PLATFORMS) + ["onboarding"]:
        dest = platforms_dir / repo
        if not dest.is_dir():
            subprocess.run(
                ["git", "clone", REPO_URL.format(repo=repo),
                 str(dest)],
                check=True,
            )
        subprocess.check_call(["git", "-C", str(dest), "fetch"])
        subprocess.check_call([
            "git", "-C",
            str(dest), "checkout", ONBOARDING_VERSION if repo == "onboarding" else "origin/main"
        ])


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


def extract_strings_from_hunk(hunk, clean=False):
    """
    Parse a diff hunk and generate (name, desc, meaning, message)
    for added GRD message elements.

    What we want:
    - any completely new unit
    - any unit where the string or metadata was changed
    What we don't want:
    - untouched (ergo already translated) units
    - broken chunks of untouched, pre-existing units
    - units that were added in a different patch (avoiding duplication)
    """
    name, message, desc, meaning = None, '', None, None
    meta_acc = ''
    had_any_additive = False

    for line in str(hunk).split('\n'):
        is_additive = line.startswith('+') or clean
        is_subtractive = line.startswith('-')
        line = line.lstrip('+').strip()

        if is_subtractive:
            continue

        if line.startswith('<message') or meta_acc:
            meta_acc += line
        elif line.startswith('</message>'):
            if name and message and had_any_additive:
                yield name, desc, meaning, message
            name, message, desc, meaning = None, '', None, None
            had_any_additive = False
        elif name:
            message += line

        if meta_acc and line.endswith('>'):
            name = get_xml_attr(meta_acc, 'name')
            desc = get_xml_attr(meta_acc, 'desc')
            meaning = get_xml_attr(meta_acc, 'meaning')
            meta_acc = ''

        had_any_additive |= bool(name) and is_additive


def to_source_format(path, name, desc, meaning, message):
    """Takes an extracted XML tuple and converts it to the JSON format."""
    context = namesub.replace_text(desc)[0]
    message = namesub.replace_text(message)[0]

    entry = {
        'name': name,
        'source': path,
        'context': context,
    }
    if meaning:
        entry['meaning'] = namesub.replace_text(meaning)[0]
    entry['message'] = message
    yield entry


def extract_strings(repo_root, platforms_dir):
    """Generate strings to be translated for all grit strings in patches."""
    for patch in get_relevant_patches(repo_root, platforms_dir):
        for hunk in patch:
            for source in extract_strings_from_hunk(hunk):
                yield from to_source_format(patch.path, *source)

    onboarding_path = platforms_dir / "onboarding" / "helium_onboarding_strings.grdp"
    if onboarding_path.exists():
        onboarding_text = onboarding_path.read_text()
        for source in extract_strings_from_hunk(onboarding_text, True):
            yield from to_source_format(
                'components/helium_onboarding/helium_onboarding_strings.grdp', *source)


def run(args, repo_root):
    """Generate the base source strings JSON from patches."""
    prep_platform_repos(args.platforms_dir)

    with open(args.output, 'w', encoding='utf-8') as out:
        data = json.dumps(
            list(extract_strings(repo_root, args.platforms_dir)),
            indent=2,
            ensure_ascii=False,
        )
        out.write(data + '\n')
