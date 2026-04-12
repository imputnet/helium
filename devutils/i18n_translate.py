"""
Translation of Helium strings using a completions API.
"""

import json
import os
from urllib.request import Request, urlopen


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


def run(args):
    """Translate source strings into target languages."""
    raise NotImplementedError("translate is not yet implemented")
