"""Top-level package for Sphinx Notebook."""

from pathlib import Path

import anytree

__author__ = """Justin Stout"""
__email__ = 'midwatch@jstout.us'
__version__ = '0.1.0'


def _render_tree(root):
    for pre, _, node in anytree.RenderTree(root):
        print(f'{pre}{node.name}')


def create_tree(src_dir):
    """Transform a list of Path() objects into a tree.

    :param src_dir: A list of Path() objects.
    :type src_dir: class: `pathlib.Path`

    :return: Tree root node.
    :rtype: anytree.Node
    """
    root = anytree.Node('root')
    parent = root

    src_dir = Path('tests/fixtures/notes')
    notes = [path.relative_to(src_dir) for path in src_dir.glob('**/*.rst')]
    notes.sort()

    for note in notes:
        for part in note.parts:

            if not anytree.find_by_attr(root, part):
                parent = anytree.Node(part, parent=parent)

            else:
                parent = anytree.find_by_attr(root, part)

        parent = root

    _render_tree(root)
