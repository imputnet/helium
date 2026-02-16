# Copyright 2025 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Util library for name_substitution.py"""

import sys


def add_grit_to_path(tree):
    """Inserts the grit/ folder into the module loading path."""
    grit_path = tree / 'tools' / 'grit'
    if not grit_path.exists():
        raise FileNotFoundError(f"grit directory not found at {grit_path}")
    sys.path.insert(0, str(grit_path))
