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
    }
    with open(index_dir / 'char_index.json', 'w', encoding='utf-8') as fh:
        json.dump(index_data, fh, ensure_ascii=False)

    data_poem = [{
        'title': 'Test Poem',
        'paragraphs': [
            '春眠不觉晓',
            '处处闻啼鸟'
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


def test_distance_options(sample_files, monkeypatch):
    tmp = sample_files
    # adjacent success
    out = run_cli(tmp, monkeypatch, [
        '--char2', '春', '--char3', '眠', '--distance', 'adjacent',
        '--index-dir', 'index'
    ])
    assert 'Test Poem (poetry)' in out
    assert highlight('春眠不觉晓', {1, 2}) in out

    # adjacent failure when not adjacent
    out = run_cli(tmp, monkeypatch, [
        '--char2', '春', '--char3', '不', '--distance', 'adjacent',
        '--index-dir', 'index'
    ])
    assert out == ''

    # sentence distance
    out = run_cli(tmp, monkeypatch, [
        '--char2', '春', '--char3', '不', '--distance', 'sentence',
        '--index-dir', 'index'
    ])
    assert highlight('春眠不觉晓', {1, 3}) in out

    # paragraph distance
    out = run_cli(tmp, monkeypatch, [
        '--char2', '春', '--char3', '处', '--distance', 'paragraph',
        '--index-dir', 'index'
    ])
    assert highlight('春眠不觉晓', {1}) in out
    assert highlight('处处闻啼鸟', {1}) in out


def test_reversible_and_tone(sample_files, monkeypatch):
    tmp = sample_files
    # reversible off - no result
    out = run_cli(tmp, monkeypatch, [
        '--char2', '处', '--char3', '春', '--distance', 'paragraph',
        '--index-dir', 'index'
    ])
    assert out == ''

    # reversible on - results printed twice
    out = run_cli(tmp, monkeypatch, [
        '--char2', '处', '--char3', '春', '--distance', 'paragraph',
        '--reversible', '--index-dir', 'index'
    ])
    line1 = highlight('春眠不觉晓', {1})
    line2 = highlight('处处闻啼鸟', {1})
    assert out.count(line1) == 2
    assert out.count(line2) == 2

    # tone filtering success
    out = run_cli(tmp, monkeypatch, [
        '--char2', '春', '--char3', '眠', '--distance', 'adjacent',
        '--tone2', '1', '--tone3', '2', '--index-dir', 'index'
    ])
    assert highlight('春眠不觉晓', {1, 2}) in out

    # tone filtering fails when tones mismatch
    out = run_cli(tmp, monkeypatch, [
        '--char2', '春', '--char3', '眠', '--distance', 'adjacent',
        '--tone2', '2', '--tone3', '2', '--index-dir', 'index'
    ])
    assert out == ''


def test_source_and_work(sample_files, monkeypatch):
    tmp = sample_files
    # filter poetry source
    out = run_cli(tmp, monkeypatch, [
        '--char2', '春', '--char3', '眠', '--distance', 'adjacent',
        '--source', 'poetry', '--index-dir', 'index'
    ])
    assert 'Test Poem (poetry)' in out
    assert 'Test Ci (ci)' not in out
    assert highlight('春眠不觉晓', {1, 2}) in out

    # filter ci source
    out = run_cli(tmp, monkeypatch, [
        '--char2', '春', '--char3', '眠', '--distance', 'adjacent',
        '--source', 'ci', '--index-dir', 'index'
    ])
    assert 'Test Ci (ci)' in out
    assert 'Test Poem (poetry)' not in out
    assert highlight('春眠不觉晓', {1, 2}) in out

    # work distance
    out = run_cli(tmp, monkeypatch, [
        '--char2', '春', '--char3', '鸟', '--distance', 'work',
        '--source', 'poetry', '--index-dir', 'index'
    ])
    assert 'Test Poem (poetry)' in out
    assert highlight('春眠不觉晓', {1}) in out
    assert highlight('处处闻啼鸟', {4}) in out

