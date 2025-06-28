import json
import os
from lib.indexer import load_index, query_char


def test_load_and_query(tmp_path):
    index_data = {
        '李': [
            {'work_id': 'w1', 'type': 'poetry', 'paragraph': 1, 'line': 1, 'pos': 1, 'tone': 3}
        ],
        '白': [
            {'work_id': 'w2', 'type': 'poetry', 'paragraph': 2, 'line': 3, 'pos': 2, 'tone': 2}
        ],
    }
    index_path = tmp_path / 'char_index.json'
    with open(index_path, 'w', encoding='utf-8') as fh:
        json.dump(index_data, fh, ensure_ascii=False)

    index = load_index(tmp_path)
    assert index == index_data

    li_hits = query_char('李', index)
    assert li_hits == index_data['李']

    unknown_hits = query_char('王', index)
    assert unknown_hits == []
