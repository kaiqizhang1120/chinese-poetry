"""Utility helpers for loading and querying the character index.

The preprocessing script ``scripts/preprocess.py`` generates an inverted
character index in JSON format. The index is stored as ``char_index.json``
inside the chosen output directory. This module provides two small helper
functions to work with that file::

    from lib.indexer import load_index, query_char

    index = load_index('./index')
    hits = query_char('李', index)

Each element returned from ``query_char`` is a dictionary describing one
occurrence of the character. The structure matches what is written by the
preprocessing script (``work_id``, ``type``, ``paragraph`` etc.).
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Any


def load_index(index_dir: str) -> Dict[str, List[Dict[str, Any]]]:
    """Load ``char_index.json`` from ``index_dir`` and return the data."""
    index_path = os.path.join(index_dir, 'char_index.json')
    with open(index_path, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def query_char(char: str, index: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Return the list of occurrences for ``char`` from the loaded index."""
    return index.get(char, [])
