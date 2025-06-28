"""Search names or characters in the poetry index."""

from __future__ import annotations

import click

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

    # TODO: implement search logic.


if __name__ == '__main__':
    main()
