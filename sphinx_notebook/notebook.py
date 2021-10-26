"""Main module."""

import re
from dataclasses import dataclass, field
from pathlib import Path

import anytree


@dataclass(order=True)
class Note:
    """Class for importing note files."""

    path: Path = field(compare=True)
    root_dir: Path

    def __str__(self):
        """Return self.path for __str__."""
        return self.path

    @property
    def parts(self):
        """Return self.path.parts."""
        return self.path.relative_to(self.root_dir).parts

    @property
    def ref_id(self):
        """Return note ref_id in note header."""
        with self.path.open(encoding="utf-8") as fd_in:
            ref = re.findall(r'\.\. _[\S]*', fd_in.read())[0]
            ref = ref[4:-1]

            return ref

    @property
    def title(self):
        """Return note title."""
        return self.path.stem


def _create_tree(notes):
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
                    parent = anytree.Node(part,
                                          parent=parent,
                                          title=note.title,
                                          ref_id=note.ref_id)

                else:
                    parent = anytree.Node(part, parent=parent)

            else:
                parent = anytree.find_by_attr(root, part)

        parent = root

    return root


def get_tree(root_dir):
    """Get a tree of notes.

    :param root_dir: The root directory of the notebook
    :type root_dir: class: `pathlib.Path`

    :return: Tree root node
    :rtype: class: anytree.Node
    """
    notes = [
        Note(root_dir=root_dir, path=path)
        for path in root_dir.glob('**/*.rst')
    ]
    notes.sort()

    return _create_tree(notes)


def render_index(root, template, out):
    """Render notebook tree into index.rst.

    :param root: notebook tree root node
    :type root: class: anytree.Node

    :param fd_out: Open file like object.
    :type fd_out: File Like Object

    :return: None
    """
    nodes = [node for node in anytree.PreOrderIter(root) if node.depth]
    out.write(template.render(nodes=nodes))
