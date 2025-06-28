"""Builds pinyin/position inverted index from Chinese poetry JSON files."""

from __future__ import annotations

import glob
import json
import os
from collections import defaultdict
from typing import Any, Dict, Iterable, List

import click
from pypinyin import Style, pinyin


def _extract_lines(entry: Dict[str, Any]) -> Iterable[str]:
    """Return the list of text lines for a poetry entry."""

    for key in ("paragraphs", "paragraph", "para", "content"):
        lines = entry.get(key)
        if lines:
            return lines
    return []


@click.command()
@click.option('--data-dir', default='./data', show_default=True,
              help='Directory containing poetry JSON files.')
@click.option('--index-dir', default='./index', show_default=True,
              help='Directory to store generated index files.')
def main(data_dir: str, index_dir: str) -> None:
    """Build the inverted index from Chinese poetry JSON files."""

    os.makedirs(index_dir, exist_ok=True)

    char_index: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    json_pattern = os.path.join(data_dir, '**', '*.json')
    json_files = glob.glob(json_pattern, recursive=True)

    for json_path in json_files:
        try:
            with open(json_path, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
        except Exception as exc:  # pragma: no cover - errors are logged
            click.echo(f'Failed to load {json_path}: {exc}', err=True)
            continue

        if not isinstance(data, list):
            continue

        for para_idx, entry in enumerate(data, start=1):
            lines = _extract_lines(entry)
            if not isinstance(lines, Iterable):
                continue

            work_id = (
                entry.get('id')
                or entry.get('uuid')
                or (
                    f"{os.path.splitext(os.path.basename(json_path))[0]}-"
                    f"{para_idx}"
                )
            )
            entry_type = 'ci' if 'rhythmic' in entry else 'poetry'

            for line_idx, line in enumerate(lines, start=1):
                if not isinstance(line, str):
                    continue
                for pos_idx, ch in enumerate(line, start=1):
                    if ch.isspace():
                        continue

                    tone_digit = 0
                    py = pinyin(ch, style=Style.TONE3, heteronym=False)
                    if py and py[0]:
                        tone_str = py[0][0]
                        digit = next(
                            (c for c in tone_str if c.isdigit()),
                            None,
                        )
                        if digit:
                            tone_digit = int(digit)

                    char_index[ch].append(
                        {
                            'work_id': work_id,
                            'type': entry_type,
                            'paragraph': para_idx,
                            'line': line_idx,
                            'pos': pos_idx,
                            'tone': tone_digit,
                        }
                    )

    index_path = os.path.join(index_dir, 'char_index.json')
    with open(index_path, 'w', encoding='utf-8') as fh:
        json.dump(char_index, fh, ensure_ascii=False, indent=2)

    click.echo(f'Char index saved to {index_path}')


if __name__ == '__main__':
    main()
