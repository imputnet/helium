#!/usr/bin/env python3
"""
Utility file for generating files for translation and
importing them into the codebase.
"""

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

PLATFORMS_DIR = Path(__file__).resolve().parent / "i18n-data"
OUT_PATH = REPO_ROOT / 'i18n' / 'source.gen.json'


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

    if args.command == 'generate':
        import i18n_generate
        return i18n_generate.run(args, REPO_ROOT)
    elif args.command == 'translate':
        import i18n_translate
        return i18n_translate.run(args)


if __name__ == '__main__':
    sys.exit(main())
