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
@click.option('--any-char3', is_flag=True,
              help='Match all possible third characters X that co-occur with --char2 in the same paragraph')
@click.option('--tone2', type=int, help='tone number for second character')
@click.option('--tone3', type=int, multiple=True,
              help='Third character tone filter; can specify multiple times, e.g. --tone3 1 --tone3 2')
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

def main(char2: str | None, char3: str | None, any_char3: bool, tone2: int | None, tone3: tuple[int, ...],
         source: tuple[str, ...], distance: str | None, reversible: bool, index_dir: str) -> None:
    """Search the character index using various options."""

    index = load_index(index_dir)

    def in_distance(o2: dict, o3: dict, dist: str) -> bool:
        if dist == 'adjacent':
            return (
                o2['work_id'] == o3['work_id']
                and o2['paragraph'] == o3['paragraph']
                and o2['line'] == o3['line']
                and abs(o2['pos'] - o3['pos']) == 1
            )
        if dist == 'sentence':
            return (
                o2['work_id'] == o3['work_id']
                and o2['paragraph'] == o3['paragraph']
                and o2['line'] == o3['line']
            )
        if dist == 'paragraph':
            return (
                o2['work_id'] == o3['work_id']
                and o2['paragraph'] == o3['paragraph']
            )
        if dist == 'work':
            return o2['work_id'] == o3['work_id']
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

    def find_matches(idx: dict, c2: str, c3: str, src: tuple[str, ...], dist: str, rev: bool) -> list[tuple[dict, dict]]:
        occs2 = [o for o in idx.get(c2, []) if not src or o['type'] in src]
        occs3 = [o for o in idx.get(c3, []) if not src or o['type'] in src]
        results: list[tuple[dict, dict]] = []
        for o2 in occs2:
            for o3 in occs3:
                if not in_distance(o2, o3, dist):
                    continue
                if not rev and not occurs_before(o2, o3):
                    continue
                pairs = [(o2, o3)] if not rev else [(o2, o3), (o3, o2)]
                results.extend(pairs)
        return results

    def print_match(match: tuple[dict, dict]) -> None:
        occ_a, occ_b = match
        entry = load_work(occ_a['work_id'])
        if not entry:
            return
        lines = extract_lines(entry)
        if not lines:
            return
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

    # Build char2 list supporting simplified/traditional forms
    if not char2:
        return
    if char2 == '乐':
        char2_list = ['乐', '樂']
    else:
        char2_list = [char2]

    # Determine possible third characters
    if any_char3:
        para_chars: dict[tuple[str, int], set[str]] = {}
        for ch, occs in index.items():
            for occ in occs:
                key = (occ['work_id'], occ['paragraph'])
                para_chars.setdefault(key, set()).add(ch)

        char3_set = set()
        for c2 in char2_list:
            for occ in index.get(c2, []):
                if source and occ['type'] not in source:
                    continue
                if occ['paragraph'] is not None:
                    char3_set.update(para_chars.get((occ['work_id'], occ['paragraph']), set()))
        char3_list = sorted(char3_set)
    else:
        if not char3:
            return
        if char3 == '乐':
            char3_list = ['乐', '樂']
        else:
            char3_list = [char3]

    # Filter char2 by tone2 if provided
    if tone2 is not None:
        filtered = []
        for c in char2_list:
            for occ in index.get(c, []):
                if occ['tone'] == tone2 and (not source or occ['type'] in source):
                    filtered.append(c)
                    break
        char2_list = sorted(set(filtered))

    # Filter char3 by tone3 if provided
    if tone3:
        filtered = []
        for c in char3_list:
            for occ in index.get(c, []):
                if occ['tone'] in tone3 and (not source or occ['type'] in source):
                    filtered.append(c)
                    break
        char3_list = sorted(set(filtered))

    # Perform search for each pair within paragraph distance
    for c2 in char2_list:
        for c3 in char3_list:
            matches = find_matches(index, c2, c3, source, 'paragraph', reversible)
            for match in matches:
                print_match(match)


if __name__ == '__main__':
    main()
