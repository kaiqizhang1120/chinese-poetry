"""Search names or characters in the poetry index."""

from __future__ import annotations

import click

import json
import os
import glob

from lib.indexer import load_index


@click.command()
@click.option('--char2', type=str, help='second character')
@click.option('--char3', type=str, help='third character')
@click.option('--tone2', type=int, help='tone number for second character')
@click.option('--tone3', type=int, help='tone number for third character')
@click.option(
    '--source',
    multiple=True,
    help='multiple: poetry, ci, shijing, etc.'
)
@click.option(
    '--distance',
    type=click.Choice(['adjacent', 'sentence', 'paragraph', 'work']),
    help='distance constraint between characters'
)
@click.option(
    '--reversible/--no-reversible',
    default=False,
    show_default=True,
    help='search characters in reverse order as well'
)
@click.option(
    '--index-dir',
    type=click.Path(),
    default='./index',
    show_default=True,
    help='directory containing the built index'
)

def main(char2: str | None, char3: str | None, tone2: int | None, tone3: int | None,
         source: tuple[str, ...], distance: str | None, reversible: bool, index_dir: str) -> None:
    """Search the character index using various options."""

    index = load_index(index_dir)

    def query_filtered(char: str | None, tone: int | None) -> list[dict]:
        if not char:
            return []
        occs = index.get(char, [])
        if tone is not None:
            occs = [o for o in occs if o.get('tone') == tone]
        if source:
            occs = [o for o in occs if o.get('type') in source]
        return occs

    occs2 = query_filtered(char2, tone2)
    occs3 = query_filtered(char3, tone3)

    def in_distance(o2: dict, o3: dict) -> bool:
        if distance == 'adjacent':
            return (
                o2['work_id'] == o3['work_id']
                and o2['paragraph'] == o3['paragraph']
                and o2['line'] == o3['line']
                and abs(o2['pos'] - o3['pos']) == 1
            )
        if distance == 'sentence':
            return (
                o2['work_id'] == o3['work_id']
                and o2['paragraph'] == o3['paragraph']
                and o2['line'] == o3['line']
            )
        if distance == 'paragraph':
            return (
                o2['work_id'] == o3['work_id']
                and o2['paragraph'] == o3['paragraph']
            )
        if distance == 'work':
            return o2['work_id'] == o3['work_id']
        # no distance specified means everything matches
        return True

    def occurs_before(a: dict, b: dict) -> bool:
        if a['work_id'] != b['work_id']:
            return False
        if a['paragraph'] != b['paragraph']:
            return a['paragraph'] < b['paragraph']
        if a['line'] != b['line']:
            return a['line'] < b['line']
        return a['pos'] < b['pos']

    def extract_lines(entry: dict) -> list[str]:
        for key in ("paragraphs", "paragraph", "para", "content"):
            lines = entry.get(key)
            if lines:
                return lines
        return []

    def load_work(work_id: str) -> dict | None:
        # work ids without explicit id usually end with '-<n>' which maps to the
        # file basename.
        if '-' in work_id and work_id.rsplit('-', 1)[1].isdigit():
            base, num = work_id.rsplit('-', 1)
            pattern = os.path.join('.', '**', f'{base}.json')
            for path in glob.glob(pattern, recursive=True):
                try:
                    with open(path, 'r', encoding='utf-8') as fh:
                        data = json.load(fh)
                    idx = int(num) - 1
                    if 0 <= idx < len(data):
                        return data[idx]
                except Exception:
                    continue
        # fallback: search for id in all files
        for path in glob.glob('./**/*.json', recursive=True):
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                if not isinstance(data, list):
                    continue
                for entry in data:
                    if (
                        isinstance(entry, dict)
                        and (entry.get('id') == work_id or entry.get('uuid') == work_id)
                    ):
                        return entry
            except Exception:
                continue
        return None

    def highlight_line(line: str, pos: set[int]) -> str:
        result = []
        for idx, ch in enumerate(line, start=1):
            if idx in pos:
                result.append(click.style(ch, fg='red'))
            else:
                result.append(ch)
        return ''.join(result)

    for o2 in occs2:
        for o3 in occs3:
            if not in_distance(o2, o3):
                continue
            if not reversible and not occurs_before(o2, o3):
                continue

            for occ_a, occ_b in ([(o2, o3)] if not reversible else [(o2, o3), (o3, o2)]):
                entry = load_work(occ_a['work_id'])
                if not entry:
                    continue
                lines = extract_lines(entry)
                if not lines:
                    continue
                title = entry.get('title') or entry.get('rhythmic') or 'Untitled'
                print(f"{title} ({occ_a['type']})")
                for idx, line in enumerate(lines, start=1):
                    if idx == occ_a['line'] == occ_b['line']:
                        print(highlight_line(line, {occ_a['pos'], occ_b['pos']}))
                    elif idx == occ_a['line']:
                        print(highlight_line(line, {occ_a['pos']}))
                    elif idx == occ_b['line']:
                        print(highlight_line(line, {occ_b['pos']}))
                    else:
                        print(line)
                print()


if __name__ == '__main__':
    main()
