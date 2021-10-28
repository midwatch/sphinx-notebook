"""Console script for Sphinx Notebook."""

import io
import sys
from pathlib import Path

import click
from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape

from sphinx_notebook import notebook

ENV = Environment(loader=PackageLoader("sphinx_notebook"),
                  autoescape=select_autoescape(),
                  trim_blocks=True)


@click.command()
@click.option('--template-dir', default=None, help="path to custom templates")
@click.argument('src')
@click.argument('dst')
def main(template_dir, src, dst):
    """Render an index.rst file for a sphinx based notebook.

    SRC: path to source directory (eg notebook/)

    DST: path to index.rst (eg build/src/index.rst)
    """
    if template_dir:
        template_index = ENV.loader = FileSystemLoader(template_dir)

    root_dir = Path(src)
    output = Path(dst)
    root = notebook.get_tree(root_dir)

    with output.open(encoding='utf-8', mode='w') as out:
        notebook.render_index(root, ENV.get_template("index.rst.jinja"), out)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
