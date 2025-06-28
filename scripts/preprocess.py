"""Builds pinyin/position inverted index from Chinese poetry JSON files."""

import click

@click.command()
@click.option('--data-dir', default='./data', show_default=True,
              help='Directory containing poetry JSON files.')
@click.option('--index-dir', default='./index', show_default=True,
              help='Directory to store generated index files.')
def main(data_dir: str, index_dir: str) -> None:
    """Build the inverted index from Chinese poetry JSON files."""
    # The actual indexing logic is intentionally left minimal.
    click.echo(f"Data directory: {data_dir}")
    click.echo(f"Index directory: {index_dir}")


if __name__ == '__main__':
    main()
