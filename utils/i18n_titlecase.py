# Copyright 2026 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Helpers for sharing translations between title-case source variants."""


def build_title_case_aliases(source):
    """Map same-scope title-case variants to the regular-case source."""
    groups = {}
    for entry in source:
        key = (entry['source'], entry['name'], entry['message'].casefold())
        groups.setdefault(key, []).append(entry)

    source_aliases = {}
    translation_aliases = {}
    for (scope, name, _), entries in groups.items():
        regular = next(
            (entry for entry in entries
             if not entry['context'].startswith('In Title Case:')),
            None,
        )
        if not regular:
            continue

        for entry in entries:
            if entry is regular or entry['message'] == regular['message']:
                continue
            source_aliases[(scope, name, entry['message'])] = regular['message']
            translation_aliases[(name, entry['message'])] = regular['message']

    return source_aliases, translation_aliases


def source_key(entry, aliases):
    """Return the canonical translation key for a source entry."""
    message = aliases.get(
        (entry['source'], entry['name'], entry['message']),
        entry['message'],
    )
    return entry['name'], message


def translation_key(entry, aliases):
    """Return the canonical translation key for a translation entry."""
    source = aliases.get((entry['name'], entry['source']), entry['source'])
    return entry['name'], source
