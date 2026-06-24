# -*- coding: UTF-8 -*-

# Copyright (c) 2019 The ungoogled-chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE.ungoogled_chromium file.

import os
import tempfile
from pathlib import Path

from .. import domain_substitution


def test_update_timestamp():
    with tempfile.TemporaryDirectory() as tmpdirname:
        path = Path(tmpdirname, 'tmp_update_timestamp')
        path.touch()
        orig_stats: os.stat_result = path.stat()

        # Add delta to timestamp
        with domain_substitution._update_timestamp(path, set_new=True):
            with path.open('w') as fileobj:
                fileobj.write('foo')

        new_stats: os.stat_result = path.stat()
        assert orig_stats.st_atime_ns != new_stats.st_atime_ns
        assert orig_stats.st_mtime_ns != new_stats.st_mtime_ns

        # Remove delta from timestamp
        with domain_substitution._update_timestamp(path, set_new=False):
            with path.open('w') as fileobj:
                fileobj.write('bar')

        new_stats: os.stat_result = path.stat()
        assert orig_stats.st_atime_ns == new_stats.st_atime_ns
        assert orig_stats.st_mtime_ns == new_stats.st_mtime_ns


def test_substitute_path_preserves_docs_and_help_hosts():
    regex_iter = domain_substitution.DomainRegexList(
        Path(__file__).parents[2] / 'domain_regex.list').regex_pairs
    content = '\n'.join((
        'https://developer.chrome.com/docs/extensions',
        'https://support.google.com/chrome?p=embedded_content',
        'https://chromestatus.com/feature/123',
        'https://www.chromestatus.com/feature/456',
        'https://accounts.google.com/signin',
        'https://chromewebstore.google.com/detail/example',
        'https://foo.developer.chrome.com/subdomain',
        'https://developer.chrome.com.evil.example/',
        'https://cruxvis.withgoogle.com/',
        'https://managedchrome.com/',
        'domain=.google.com',
        'domain=.support.google.com',
    ))

    with tempfile.TemporaryDirectory() as tmpdirname:
        path = Path(tmpdirname, 'domains.txt')
        path.write_text(content, encoding='UTF-8')

        crc32_hash, orig_content = domain_substitution._substitute_path(path, regex_iter)

        assert crc32_hash is not None
        assert orig_content == content.encode('UTF-8')
        assert path.read_text(encoding='UTF-8') == '\n'.join((
            'https://developer.chrome.com/docs/extensions',
            'https://support.google.com/chrome?p=embedded_content',
            'https://chromestatus.com/feature/123',
            'https://www.chromestatus.com/feature/456',
            'https://accounts.9oo91e.qjz9zk/signin',
            'https://chromewebstore.9oo91e.qjz9zk/detail/example',
            'https://foo.developer.ch40me.qjz9zk/subdomain',
            'https://developer.ch40me.qjz9zk.evil.example/',
            'https://cruxvis.with9oo91e.qjz9zk/',
            'https://managedch40me.qjz9zk/',
            'domain=.9oo91e.qjz9zk',
            'domain=.support.google.com',
        ))


def test_substitute_path_skips_cache_when_only_preserved_hosts_match():
    regex_iter = domain_substitution.DomainRegexList(
        Path(__file__).parents[2] / 'domain_regex.list').regex_pairs
    content = '\n'.join((
        'https://developer.chrome.com',
        'https://support.google.com',
        'https://chromestatus.com',
        'https://www.chromestatus.com',
    ))

    with tempfile.TemporaryDirectory() as tmpdirname:
        path = Path(tmpdirname, 'domains.txt')
        path.write_text(content, encoding='UTF-8')

        crc32_hash, orig_content = domain_substitution._substitute_path(path, regex_iter)

        assert crc32_hash is None
        assert orig_content is None
        assert path.read_text(encoding='UTF-8') == content
