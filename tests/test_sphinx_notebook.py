#!/usr/bin/env python
"""Tests for `media_hoard_cli` package."""
# pylint: disable=redefined-outer-name
import dataclasses
from pathlib import Path

from sphinx_notebook import notebook
from sphinx_notebook import util


def test_get_title():
    """Test extract title from note."""
    path =  Path('tests/fixtures/notes/simple/cad_cam_make/my_cad_note.rst')

    expected = 'My CAD Note'
    result = util.get_title(path)

    assert expected == result


def test_parse_stem():
    """Test parse note stem."""

    stems = [
        'my_note', '0__my_note', 'checklist__my_note', 'checklist__0__my_note',
        'two_part__0__my_note', 'two_part__my_note'
    ]

    expected = ['', '', 'checklist', 'checklist', 'two_part', 'two_part']

    results = [util.parse_stem(x) for x in stems]  # pylint: disable=protected-access

    assert expected == results


def test_meta_data():
    root_dir = Path('tests/fixtures/notes/simple')
    path = root_dir / Path('_meta.yaml')
    expected = {'title': "Simple Notebook", 'header': "Simple Notebook Header", 'name': '.'}

    meta_data = notebook.MetaData.from_yaml(root_dir, path)
    assert expected == dataclasses.asdict(meta_data)

    path = root_dir / Path('cad_cam_make/_meta.yaml')
    expected = {'title': "CAD/CAM/MAKE", 'header': '', 'name': 'Cad Cam Make'}

    meta_data = notebook.MetaData.from_yaml(root_dir, path)
    assert expected == dataclasses.asdict(meta_data)


def test_note():
    """Test Note class."""
    root_dir = Path('tests/fixtures/notes/simple/')
    path = root_dir / 'cad_cam_make/my_cad_note.rst'

    note = notebook.Note(root_dir, path)

    assert note.group == ''
    assert note.url == '/cad_cam_make/my_cad_note'
    assert note.title == 'My CAD Note'
    assert note.parents == ['Cad Cam Make']
