"""Template Filters."""
from itertools import groupby, zip_longest

from jinja2.filters import do_batch


def format_rst(cell):
    """Format cell for rst list table."""
    if cell:
        return f':doc:`{cell.title} <{cell.url}>`'

    return ""


def table_header(notes):
    """Return table header row."""
    return {x.group for x in notes if x.group}


def table_body(notes):
    """Return table rows."""
    if not table_header(notes):
        return do_batch(notes, 4, fill_with="")

    cols = []
    for _, col in groupby(notes, lambda x: x.group):
        cols.append(list(col))

    return zip_longest(*cols, fillvalue=None)
