"""Console script for Sphinx Notebook."""

import io
import sys
from pathlib import Path

import click

import sphinx_notebook

SRC_DIR = Path('tests/fixtures/notes')


@click.command()
def main():
    """Console script for sphinx_notebook."""
    # click.echo("Replace this message by putting your code into "
    #            "sphinx_notebook.cli.main")
    # click.echo("See click documentation at https://click.palletsprojects.com/")
    notes = [sphinx_notebook.Note(src_dir=SRC_DIR, path=path) for path in SRC_DIR.glob('**/*.rst')]
    notes.sort()

    # for note in notes:
    #     print(f'{note.title} - {note.ref_id}')

    root = sphinx_notebook.create_tree(notes)

    output = io.StringIO()
    sphinx_notebook.render_index(root, output)
    output.seek(0)

    print(output.read())

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
