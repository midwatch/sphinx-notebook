"""Console script for Sphinx Notebook."""

import io
import sys
from pathlib import Path

import click
from jinja2 import Environment, PackageLoader, select_autoescape

from sphinx_notebook import notebook

ROOT_DIR = Path('tests/fixtures/notes')

ENV = Environment(loader=PackageLoader("sphinx_notebook"),
                  autoescape=select_autoescape(),
                  trim_blocks=True)


@click.command()
def main():
    """Console script for sphinx_notebook."""
    # click.echo("Replace this message by putting your code into "
    #            "sphinx_notebook.cli.main")
    # click.echo("See click documentation at https://click.palletsprojects.com/")
    """
    from sphinx_notebook inport notebook

    root = notebook.get_tree(SRC_DIR)
    notebook.update_tree(root, config) # future

    with Path('build/rst/index.rst').open('w', encoding='utf8') as out:
        notebook.render_index(root, template, out)

    notebook.add_note(path, template='xxx.rst')
    """
    root = notebook.get_tree(ROOT_DIR)

    output = io.StringIO()
    notebook.render_index(root, ENV.get_template("index.rst"), output)
    output.seek(0)

    # click.echo(output.read())
    print(output.read())

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
