"""Console script for Sphinx Notebook."""

import sys
from pathlib import Path

import click
from jinja2 import (Environment, FileSystemLoader, PackageLoader,
                    select_autoescape)

from sphinx_notebook import notebook

ENV = Environment(loader=PackageLoader("sphinx_notebook"),
                  autoescape=select_autoescape(),
                  trim_blocks=True)


@click.group()
def main():
    """Empty click anchor function."""


@click.command()
@click.option('--template-dir', default=None, help="path to custom templates")
@click.option('--template-name',
              default='index.rst.jinja',
              help="Use alt index template")
@click.argument('src')
@click.argument('dst')
def build(template_dir, template_name, src, dst):
    """Render an index.rst file for a sphinx based notebook.

    SRC: path to source directory (eg notebook/)

    DST: path to index.rst (eg build/src/index.rst)
    """
    if template_dir:
        ENV.loader = FileSystemLoader(template_dir)

    root_dir = Path(src)
    output = Path(dst)
    root = notebook.get_tree(root_dir)

    with output.open(encoding='utf-8', mode='w') as out:
        notebook.render_index(root, ENV.get_template(template_name), out)

    return 0


@click.command()
@click.option('--template-dir', default=None, help="path to custom templates")
@click.option('--template-name',
              default='note.rst.jinja',
              help="Use alt note template")
@click.argument('dst')
def new(template_dir, template_name, dst):
    """Add a new note from a template.

    DST: path to note.rst (eg notebook/section_1/sub_section_1/topic_1.rst)
    """
    if template_dir:
        ENV.loader = FileSystemLoader(template_dir)

    output = Path(dst)

    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open(encoding='utf-8', mode='w') as out:
        notebook.render_note(ENV.get_template(template_name), out)

    return 0


main.add_command(build)
main.add_command(new)

if __name__ == "__main__":
    sys.exit(main())  # pylint: disable=no-value-for-parameter
