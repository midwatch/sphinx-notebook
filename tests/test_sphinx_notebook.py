#!/usr/bin/env python
"""Tests for `sphinx_notebook` package."""
# pylint: disable=redefined-outer-name
from pathlib import Path

# import pytest
from anytree import search

from sphinx_notebook import notebook

# from click.testing import CliRunner

ID_README_3 = 'U12uzOMtKg'


def test_render_sub_section():
    """Test failure to render section readme files. regression."""
    root_dir = Path('tests/fixtures/notes')
    notes = [
        notebook.Note(root_dir=root_dir, path=path)
        for path in root_dir.glob('**/*.rst')
    ]

    root = notebook._create_tree(notes)  # pylint: disable=protected-access
    assert search.find_by_attr(root, name="ref_id", value=ID_README_3)


# def test_command_line_interface():
#     """Test the CLI."""
#     runner = CliRunner()
#     result = runner.invoke(cli.main)
#     assert result.exit_code == 0
#     assert 'sphinx_notebook.cli.main' in result.output
#     help_result = runner.invoke(cli.main, ['--help'])
#     assert help_result.exit_code == 0
#     assert '--help  Show this message and exit.' in help_result.output
