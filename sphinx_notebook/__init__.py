"""Top-level package for Sphinx Notebook."""

import re
from pathlib import Path
from dataclasses import dataclass
from dataclasses import field

import anytree

__author__ = """Justin Stout"""
__email__ = 'midwatch@jstout.us'
__version__ = '0.1.0'

SEPERATORS = ['', '=', '-', '~']


@dataclass(order=True)
class Note:
    """Class for importing note files."""
    path: Path = field(compare=True)
    src_dir: Path

    def __str__(self):
        return self.path

    @property
    def parts(self):
        return self.path.relative_to(self.src_dir).parts

    @property
    def ref_id(self):
        with self.path.open() as fd_in:
            ref = re.findall(r'\.\. _[\S]*', fd_in.read())[0]
            ref = ref[4:-1]

            return ref

    @property
    def title(self):
        return self.path.stem


def _render_table(leafs, fd_out):
    """Render a table of leafs as rst table."""

    if not leafs:
        return

    fd_out.write('.. list-table::\n')
    fd_out.write('\n')

    for leaf in leafs:
        fd_out.write(f'\t* - :ref:`{leaf.title} <{leaf.ref_id}>`\n')


def _render_tree(root):
    for pre, _, node in anytree.RenderTree(root):
        print(f'{pre}{node.name}')


def create_tree(notes):
    """Transform a list of objects into a tree.

    :param notes: A list of Path() objects.
    :type notes: list: `Note`

    :return: Tree root node.
    :rtype: anytree.Node
    """
    root = anytree.Node('root')
    parent = root

    for note in notes:
        for part in note.parts:
            if not anytree.find_by_attr(root, part):
                if '.rst' in part:
                    parent = anytree.Node(part, parent=parent, title=note.title, ref_id=note.ref_id)

                else:
                    parent = anytree.Node(part, parent=parent)

            else:
                parent = anytree.find_by_attr(root, part)

        parent = root

    return root


def render_index(root, fd_out):
    """Render notebook tree into index.rst

    :param root: notebook tree root node
    :type root: class: anytree.Node

    :param fd_out: Open file object.
    :type fd_out: File Like Object

    :return: None
    """
    for node in anytree.PreOrderIter(root):
        if node.depth and not node.is_leaf:
            fd_out.write(f'{node.name}\n')
            fd_out.write(f'{SEPERATORS[node.depth]*20}\n')
            fd_out.write('\n')

            _render_table([x for x in node.children if x.is_leaf], fd_out)

        fd_out.write('\n')

    return fd_out
