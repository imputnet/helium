#!/usr/bin/env python3
"""
Utility file for generating files for translation and
importing them into the codebase.
"""

import xml.etree.ElementTree as xml
import subprocess
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import utils.name_substitution_utils as namesub
from third_party import unidiff

PLATFORMS = ("windows", "macos", "linux")
REPO_URL = "https://github.com/imputnet/helium-{platform}.git"
PLATFORMS_DIR = Path(__file__).resolve().parent / "i18n-data"
REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = REPO_ROOT / 'i18n' / 'source.gen.json'


def get_id(name, context, text):
    """Compute the fingerprint ID for a GRD message element."""
    message = xml.fromstring(f'<message name="{name}" desc="{context}">{text}</message>')
    return namesub.compute_fp(message)


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


def get_patch_paths():
    """
    Generate patch file paths from all series files (main repo + platforms).
    """
    series_files = [REPO_ROOT / "patches" / "series"] + \
        [PLATFORMS_DIR / platform / "patches" / "series" for platform in PLATFORMS]

    for series_file in series_files:
        patches_dir = series_file.parent
        for line in series_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            yield str(patches_dir / line.split()[0])


def get_relevant_patches():
    """Generate patched hunks from patches that touch .grd or .grdp files."""
    for path in get_patch_paths():
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


def extract_strings():
    """Generate strings to be translated for all grit strings in patches."""
    for patch in get_relevant_patches():
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


def cmd_generate_base(args):
    """Generate the base source strings JSON from patches."""
    prep_platform_repos(args.platforms_dir)
    namesub.add_grit_to_path(args.tree)

    with open(args.output, 'w', encoding='utf-8') as out:
        out.write(json.dumps(list(extract_strings()), indent=2, ensure_ascii=False))
        out.write('\n')


def cmd_translate(args):
    """Translate source strings into target languages."""
    raise NotImplementedError("translate is not yet implemented")


def parse_args():
    """CLI arg parsing"""
    parser = argparse.ArgumentParser(description='i18n tooling for Helium')
    subparsers = parser.add_subparsers(dest='command', required=True)
    base = subparsers.add_parser('generate',
                                 help='Extract translatable strings from patches')
    base.add_argument('-t',
                      '--tree',
                      type=Path,
                      required=True,
                      help='Path to Chromium source tree')
    base.add_argument('-p',
                      '--platforms-dir',
                      type=Path,
                      default=PLATFORMS_DIR,
                      help='Path where platform repos will be cloned')
    base.add_argument('-o',
                      '--output',
                      type=Path,
                      default=OUT_PATH,
                      help='Output path where base JSON file will be saved')

    translate = subparsers.add_parser('translate',
                                      help='Translate source strings into target languages')
    translate.add_argument('-l',
                           '--language',
                           type=str,
                           help='Target language code (e.g. "fr"). '
                                'If omitted, translates all languages.')

    return parser.parse_args()


def main():
    """CLI entrypoint"""
    args = parse_args()
    commands = {
        'generate': cmd_generate_base,
        'translate': cmd_translate,
    }
    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
