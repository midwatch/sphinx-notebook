"""Console script for Sphinx Notebook."""
import os
import sys
from pathlib import Path

import click
import yaml
from jinja2 import (Environment, FileSystemLoader, PackageLoader,
                    select_autoescape)

from sphinx_notebook import filters, notebook

ENV = Environment(loader=PackageLoader("sphinx_notebook"),
                  autoescape=select_autoescape(),
                  trim_blocks=True)
ENV.filters["to_table"] = filters.to_table


@click.group()
@click.version_option(version='0.8.1')
def main():
    """Empty click anchor function."""

@click.group()
def new():
    """Empty click anchor function."""


@click.command()
@click.option('--prune', multiple=True)
@click.option('--template-dir', default=None, help="path to custom templates")
@click.option('--template-name',
              default='index.rst.jinja',
              help="Use alt index template")
@click.argument('src')
@click.argument('dst')
def build(prune, template_dir, template_name, src, dst):  # pylint: disable=too-many-arguments
    """Render an index.rst file for a sphinx based notebook.

    SRC: path to source directory (eg notebook/)

    DST: path to index.rst (eg build/src/index.rst)
    """
    if template_dir:
        ENV.loader = FileSystemLoader(template_dir)

    root_dir = Path(src)
    output = Path(dst)

    root = notebook.get_tree(root_dir)
    notebook.prune_tree(root, prune)
    notebook.update_meta_data(root_dir, root)

    with (root_dir / '_meta.yaml').open() as fd_in:
        meta_data =  yaml.safe_load(fd_in)

        with output.open(encoding='utf-8', mode='w') as out:
            notebook.render_index(root, meta_data['title'], meta_data['header'],
                                  ENV.get_template(template_name), out)

    return 0


@click.command()
@click.option('--template-dir', default=None, help="path to custom templates")
@click.option('--template-name',
              default='note.rst.jinja',
              help="Use alt note template")
@click.argument('dst')
def new_note(template_dir, template_name, dst):
    """Add a new note from a template.

    DST: path to note.rst (eg notebook/section_1/sub_section_1/topic_1.rst)
    """
    if template_dir:
        ENV.loader = FileSystemLoader(template_dir)

    output = Path(dst)

    output.parent.mkdir(parents=True, exist_ok=True)

    try:
        with output.open(encoding='utf-8', mode='x') as out:
            notebook.render_note(ENV.get_template(template_name), out)

    except FileExistsError as file_exists:
        raise click.FileError(output, 'file exists') from file_exists

    return 0


@click.command()
@click.option('--count', default=1, help='number of targets to generate')
def new_target(count):
    """Generate a new target using NanoID."""
    for _ in range(count):
        click.echo(notebook.get_target())


new.add_command(new_note, name='note')
new.add_command(new_target, name='target')

main.add_command(build)
main.add_command(new)

if __name__ == "__main__":
    sys.exit(main())  # pylint: disable=no-value-for-parameter
