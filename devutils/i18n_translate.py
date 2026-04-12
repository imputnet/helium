"""
Translation of Helium strings using a completions API.
"""

import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

I18N_DIR = Path(__file__).resolve().parent.parent / 'i18n'
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
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': data},
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


def load_existing(lang_code):
    """Load existing translations for a language, or empty dict."""
    path = TRANSLATIONS_DIR / f'{lang_code}.json'
    if path.exists():
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return {}


def find_untranslated(source, existing):
    """
    Return indices into source for strings that need (re)translation.
    A string needs translation if:
    - it has no entry in existing translations, or
    - the source message has changed since it was last translated
    """
    indices = []
    for i, entry in enumerate(source):
        name = entry['name']
        prev = existing.get(name)
        if not prev or prev.get('source') != entry['message']:
            indices.append(i)
    return indices


def build_payload(source, untranslated, existing, context_window=2):
    """
    Build the JSON array to send to the model.
    Includes untranslated strings plus nearby neighbors as context.
    Context-only strings are marked with "translate": false.
    """

    needed = set(untranslated)
    all_indices = set()
    for i in untranslated:
        for offset in range(-context_window, context_window + 1):
            idx = i + offset
            if 0 <= idx < len(source):
                all_indices.add(idx)

    payload = []
    for i in sorted(all_indices):
        entry = {
            'name': source[i]['name'],
            'context': source[i]['context'],
            'message': source[i]['message'],
        }
        if i not in needed:
            prev = existing[source[i]['name']]
            entry['translate'] = False
            entry['translation'] = prev['message']
        payload.append(entry)

    return payload


def fill_prompt(template, language_name, language_code):
    """Fill in the language placeholders in a prompt template."""
    return (template
            .replace('{{language_name}}', language_name)
            .replace('{{language_code}}', language_code))


def save_translations(lang_code, source, existing, response):
    """Merge model response into existing translations and save."""
    source_by_name = {s['name']: s['message'] for s in source}

    for entry in response:
        name = entry['name']
        result = {
            'source': source_by_name[name],
            'message': entry['message'],
        }
        if 'feminine' in entry:
            result['feminine'] = entry['feminine']
        if 'masculine' in entry:
            result['masculine'] = entry['masculine']
        existing[name] = result

    path = TRANSLATIONS_DIR / f'{lang_code}.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)
        f.write('\n')


def translate_language(lang_code, lang_name, source, prompt_template):
    """Run translation for a single language."""
    existing = load_existing(lang_code)
    untranslated = find_untranslated(source, existing)

    if not untranslated:
        print(f'{lang_code}: already up to date')
        return

    print(f'{lang_code}: {len(untranslated)} strings to translate')

    payload = build_payload(source, untranslated, existing)
    prompt = fill_prompt(prompt_template, lang_name, lang_code)
    data = json.dumps(payload, ensure_ascii=False)

    raw = llm_chat(prompt, data)
    response = json.loads(raw)

    save_translations(lang_code, source, existing, response)
    print(f'{lang_code}: done')


def run(args):
    """Translate source strings into target languages."""
    with open(SOURCE_PATH, encoding='utf-8') as f:
        source = json.load(f)
    with open(I18N_DIR / 'languages.json', encoding='utf-8') as f:
        languages = json.load(f)

    prompt_template = (I18N_DIR / 'prompt.md').read_text(encoding='utf-8')
    TRANSLATIONS_DIR.mkdir(parents=True, exist_ok=True)

    if args.language:
        if args.language not in languages:
            raise ValueError(f'unknown language code: {args.language}')
        translate_language(args.language, languages[args.language], source, prompt_template)
    else:
        for code, name in languages.items():
            translate_language(code, name, source, prompt_template)
