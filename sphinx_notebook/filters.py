"""Template Filters."""
from itertools import zip_longest

def to_table(value):

    header = []
    nodes = []

    for group, items in value:
        header.append(group)
        nodes.append(items)

    retval = [header]

    for row in zip_longest(*nodes):
        retval.append(row)

    return retval
