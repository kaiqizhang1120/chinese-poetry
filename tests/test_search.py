import json
import os

import pytest
from click.testing import CliRunner

from scripts import search


def highlight(line: str, positions: set[int]) -> str:
    from click import style
    return ''.join(style(ch, fg='red') if i in positions else ch for i, ch in enumerate(line, 1))


@pytest.fixture()
def sample_files(tmp_path):
    index_dir = tmp_path / 'index'
    index_dir.mkdir()
    index_data = {
        '春': [
            {
                'work_id': 'poem-1', 'type': 'poetry', 'paragraph': 1,
                'line': 1, 'pos': 1, 'tone': 1
            },
            {
                'work_id': 'ci-1', 'type': 'ci', 'paragraph': 1,
                'line': 1, 'pos': 1, 'tone': 1
            }
        ],
        '眠': [
            {
                'work_id': 'poem-1', 'type': 'poetry', 'paragraph': 1,
                'line': 1, 'pos': 2, 'tone': 2
            },
            {
                'work_id': 'ci-1', 'type': 'ci', 'paragraph': 1,
                'line': 1, 'pos': 2, 'tone': 2
            },
            {
                'work_id': 'poem-2', 'type': 'poetry', 'paragraph': 1,
                'line': 1, 'pos': 2, 'tone': 2
            },
            {
                'work_id': 'poem-2', 'type': 'poetry', 'paragraph': 2,
                'line': 2, 'pos': 1, 'tone': 2
            }
        ],
        '不': [{
            'work_id': 'poem-1', 'type': 'poetry', 'paragraph': 1,
            'line': 1, 'pos': 3, 'tone': 4
        }],
        '处': [{
            'work_id': 'poem-1', 'type': 'poetry', 'paragraph': 1,
            'line': 2, 'pos': 1, 'tone': 3
        }],
        '鸟': [{
            'work_id': 'poem-1', 'type': 'poetry', 'paragraph': 1,
            'line': 2, 'pos': 4, 'tone': 3
        }],
        '乐': [{
            'work_id': 'poem-2', 'type': 'poetry', 'paragraph': 1,
            'line': 1, 'pos': 1, 'tone': 4
        }],
        '樂': [{
            'work_id': 'poem-2', 'type': 'poetry', 'paragraph': 2,
            'line': 2, 'pos': 2, 'tone': 4
        }],
    }
    with open(index_dir / 'char_index.json', 'w', encoding='utf-8') as fh:
        json.dump(index_data, fh, ensure_ascii=False)

    data_poem = [{
        'title': 'Test Poem',
        'paragraphs': [
            '春眠不觉晓',
            '处处闻啼鸟'
        ]
    }, {
        'title': 'Le Poem',
        'paragraphs': [
            '乐眠',
            '眠樂'
        ]
    }]
    with open(tmp_path / 'poem.json', 'w', encoding='utf-8') as fh:
        json.dump(data_poem, fh, ensure_ascii=False)

    data_ci = [{
        'rhythmic': 'Test Ci',
        'paragraphs': [
            '春眠不觉晓',
            '处处闻啼鸟'
        ]
    }]
    with open(tmp_path / 'ci.json', 'w', encoding='utf-8') as fh:
        json.dump(data_ci, fh, ensure_ascii=False)
    return tmp_path


def run_cli(tmp_path, monkeypatch, args):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(search.main, args)
    assert result.exit_code == 0
    return result.output


def test_basic_le_search(sample_files, monkeypatch):
    tmp = sample_files
    out = run_cli(tmp, monkeypatch, [
        '--char2', '乐', '--char3', '眠', '--tone3', '2', '--index-dir', 'index'
    ])
    assert 'Le Poem (poetry)' in out
    assert highlight('乐眠', {1, 2}) in out


def test_traditional_reversible(sample_files, monkeypatch):
    tmp = sample_files
    out = run_cli(tmp, monkeypatch, [
        '--char2', '樂', '--char3', '眠', '--reversible', '--tone3', '2',
        '--index-dir', 'index'
    ])
    assert highlight('眠樂', {1, 2}) in out


def test_any_char3(sample_files, monkeypatch):
    tmp = sample_files
    out = run_cli(tmp, monkeypatch, [
        '--char2', '乐', '--any-char3', '--tone3', '1', '--tone3', '2',
        '--index-dir', 'index'
    ])
    assert highlight('乐眠', {1, 2}) in out



