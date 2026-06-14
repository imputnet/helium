# Copyright 2026 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""
Translation of Helium strings using an LLM backend.
"""

import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parent.parent

from i18n_titlecase import (
    build_title_case_aliases,
    source_key,
    translation_key,
)

I18N_DIR = REPO_ROOT / 'i18n'
SOURCE_PATH = I18N_DIR / 'source.gen.json'
TRANSLATIONS_DIR = I18N_DIR / 'translations'


def llm_chat(prompt, data):
    """Send a chat completion request to a completions API."""
    base_url = os.environ.get('LLM_BASE_URL')
    api_key = os.environ.get('LLM_API_KEY')
    model = os.environ.get('LLM_MODEL')

    if not base_url:
        raise RuntimeError('LLM_BASE_URL is not set')
    if not api_key:
        raise RuntimeError('LLM_API_KEY is not set')
    if not model:
        raise RuntimeError('LLM_MODEL is not set')

    req = Request(
        f'{base_url.rstrip("/")}/chat/completions',
        data=json.dumps({
            'model': model,
            'messages': [
                {
                    'role': 'system',
                    'content': prompt
                },
                {
                    'role': 'user',
                    'content': data
                },
            ],
        }).encode(),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        },
    )

    with urlopen(req) as resp:
        body = json.loads(resp.read())

    return body['choices'][0]['message']['content']


def run_command(cmd, data):
    """Run a non-interactive CLI backend."""
    with tempfile.TemporaryDirectory(prefix='helium-i18n-cmd-') as cwd:
        try:
            proc = subprocess.run(cmd,
                                  input=data,
                                  text=True,
                                  capture_output=True,
                                  check=True,
                                  cwd=cwd)
        except FileNotFoundError as exc:
            raise RuntimeError(f'{cmd[0]} executable not found') from exc
        except subprocess.CalledProcessError as exc:
            details = []
            if exc.stderr:
                details.append(exc.stderr.strip())
            if exc.stdout:
                details.append(f'stdout:\n{exc.stdout.strip()}')
            message = f'{cmd[0]} failed'
            if details:
                message += ':\n' + '\n'.join(details)
            raise RuntimeError(message) from exc

    return proc.stdout


def command_chat(prompt, data, command):
    """Send a translation request through a provided command."""
    cmd = shlex.split(command)
    if not cmd:
        raise ValueError('--cmd must not be empty')

    cmd.append(prompt)
    return run_command(cmd, data)


def translate_with_backend(prompt, data, command=None):
    """Send a translation request to the selected backend."""
    if command:
        return command_chat(prompt, data, command)
    return llm_chat(prompt, data)


def load_existing(lang_code, translation_aliases):
    """Load existing translations as a dict keyed by (name, source)."""
    path = TRANSLATIONS_DIR / f'{lang_code}.json'
    if not path.exists():
        return {}
    with open(path, encoding='utf-8') as file:
        entries = json.load(file)
    result = {}
    for entry in entries:
        if entry:
            key = translation_key(entry, translation_aliases)
            entry = dict(entry)
            is_alias = entry['source'] != key[1]
            entry['source'] = key[1]
            if key not in result or not is_alias:
                result[key] = entry
    return result


def find_untranslated(source, existing, source_aliases):
    """
    Return indices into source for strings that need (re)translation.
    A string needs translation if:
    - it has no existing translation, or
    - the source message has changed since it was last translated
    """
    indices = []
    for i, entry in enumerate(source):
        key = source_key(entry, source_aliases)
        if key not in existing:
            indices.append(i)
    return indices


def build_payload(source, untranslated, existing, source_aliases, context_window=2):
    """
    Build the JSON array to send to the model.
    Includes untranslated strings plus nearby neighbors as context.
    Context-only strings are marked with "translate": false.

    Deduplicates untranslated entries with identical name + message,
    returning a dedup_map that maps each payload index to all source
    indices sharing that name + message.
    """
    needed = set(untranslated)
    all_indices = set()
    for i in untranslated:
        for offset in range(-context_window, context_window + 1):
            idx = i + offset
            if 0 <= idx < len(source):
                all_indices.add(idx)

    # group untranslated indices by canonical (name, message) for dedup
    seen = {}
    for i in untranslated:
        key = source_key(source[i], source_aliases)
        seen.setdefault(key, []).append(i)

    payload = []
    dedup_map = []
    added_keys = set()
    for i in sorted(all_indices):
        if i not in needed:
            key = source_key(source[i], source_aliases)
            entry = {
                'name': source[i]['name'],
                'context': source[i]['context'],
                'message': source[i]['message'],
                'translate': False,
                'translation': existing[key]['message'],
            }
            payload.append(entry)
            continue

        key = source_key(source[i], source_aliases)
        if key in added_keys:
            continue
        added_keys.add(key)

        rep_idx = next(
            (idx for idx in seen[key] if source[idx]['message'] == key[1]),
            seen[key][0],
        )
        entry = {
            'name': source[rep_idx]['name'],
            'context': source[rep_idx]['context'],
            'message': source[rep_idx]['message'],
        }
        payload.append(entry)
        dedup_map.append(seen[key])

    return payload, dedup_map


def fill_prompt(template, language_name, language_code):
    """Fill in the language placeholders in a prompt template."""
    template = template.replace('{{language_name}}', language_name)
    template = template.replace('{{language_code}}', language_code)
    return template


def fixup_json(raw):
    """Strips markdown code fences and fixes unescaped double quotes."""
    raw = raw.strip()
    raw = re.sub(r'^```(?:json)?\s*\n?', '', raw)
    raw = re.sub(r'\n?```\s*$', '', raw)

    result = []
    in_string = False
    i = 0
    while i < len(raw):
        char = raw[i]
        if char == '\\' and in_string:
            # skip escaped character
            result.append(raw[i:i + 2])
            i += 2
            continue
        if char == '"':
            if not in_string:
                in_string = True
                result.append(char)
            elif i + 1 < len(raw) and raw[i + 1] not in (',', '}', ']', ':', '\n', '\r', ' ', '\t'):
                # quote not followed by a structural character — escape it
                result.append('\\"')
            else:
                in_string = False
                result.append(char)
        else:
            result.append(char)
        i += 1
    return ''.join(result)


def parse_response(raw, expected_names):
    """Parse and validate the model's response."""
    raw = fixup_json(raw)

    try:
        response = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f'failed to parse model response: {exc}', file=sys.stderr)
        print(f'raw response:\n{raw}', file=sys.stderr)
        raise

    if not isinstance(response, list):
        raise ValueError('expected a JSON array from the model')

    allowed_keys = {'name', 'message', 'feminine', 'masculine'}

    results = []
    for entry in response:
        if not isinstance(entry, dict):
            raise ValueError(f'expected object in array, got {type(entry).__name__}')

        if 'name' not in entry or 'message' not in entry:
            raise ValueError(f'entry missing required fields: {entry}')

        if entry['name'] not in expected_names:
            continue

        extra = set(entry.keys()) - allowed_keys
        if extra:
            raise ValueError(f'unexpected fields in entry {entry["name"]}: {extra}')

        results.append(entry)

    missing = expected_names - {e['name'] for e in results}
    if missing:
        raise ValueError(f'model did not translate: {missing}')

    return results


def save_translations(lang_code, source, existing, response, dedup_map, source_aliases):
    """Merge model response into existing translations and save."""
    for entry, indices in zip(response, dedup_map):
        expected_name = source[indices[0]]['name']
        if entry['name'] != expected_name:
            raise ValueError(f'response order mismatch at index {indices[0]}: '
                             f'expected {expected_name}, got {entry["name"]}')
        for src_idx in indices:
            key = source_key(source[src_idx], source_aliases)
            result = {
                'name': source[src_idx]['name'],
                'source': key[1],
                'message': entry['message'],
            }
            if 'feminine' in entry:
                result['feminine'] = entry['feminine']
            if 'masculine' in entry:
                result['masculine'] = entry['masculine']
            existing[key] = result

    path = TRANSLATIONS_DIR / f'{lang_code}.json'
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(list(existing.values()), file, indent=2, ensure_ascii=False)
        file.write('\n')


# pylint: disable-next=too-many-locals
def translate_language(language, source, prompt_template, from_file=None, command=None):
    """Run translation for a single language."""
    lang_code, lang_name = language
    source_aliases, translation_aliases = build_title_case_aliases(source)
    existing = load_existing(lang_code, translation_aliases)
    untranslated = find_untranslated(source, existing, source_aliases)

    if not untranslated:
        print(f'{lang_code}: already up to date')
        return

    print(f'{lang_code}: {len(untranslated)} strings to translate')

    payload, dedup_map = build_payload(source, untranslated, existing, source_aliases)
    expected_names = {source[i]['name'] for i in untranslated}

    if from_file:
        if str(from_file) == '-':
            raw = sys.stdin.read()
        else:
            raw = from_file.read_text(encoding='utf-8')
    else:
        prompt = fill_prompt(prompt_template, lang_name, lang_code)
        data = json.dumps(payload, ensure_ascii=False)
        raw = translate_with_backend(prompt, data, command)

    response = parse_response(raw, expected_names)

    save_translations(lang_code, source, existing, response, dedup_map, source_aliases)
    print(f'{lang_code}: done')


def run(args):
    """Translate source strings into target languages."""
    with open(SOURCE_PATH, encoding='utf-8') as file:
        source = json.load(file)
    with open(I18N_DIR / 'languages.json', encoding='utf-8') as file:
        languages = json.load(file)

    prompt_template = (I18N_DIR / 'prompt.md').read_text(encoding='utf-8')
    TRANSLATIONS_DIR.mkdir(parents=True, exist_ok=True)

    language = getattr(args, 'language', None)
    from_file = getattr(args, 'from_file', None)
    command = getattr(args, 'cmd', None)

    if not command:
        command = os.environ.get('I18N_TRANSLATE_CMD')

    if language:
        for code in language:
            if code not in languages:
                raise ValueError(f'unknown language code: {code}')
            translate_language((code, languages[code]), source, prompt_template, from_file, command)
    else:
        if from_file:
            raise ValueError('--from-file requires --language')
        for code, name in languages.items():
            translate_language((code, name), source, prompt_template, command=command)
