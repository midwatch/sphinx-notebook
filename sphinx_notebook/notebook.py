"""Main module."""

import re
from dataclasses import dataclass, field
from itertools import chain
from pathlib import Path

import anytree
import nanoid

NANOID_ALPHABET = '-0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
NANOID_SIZE = 10


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
        title = self.path.stem
        with self.path.open(encoding="utf-8") as fd_in:
            found_line = False

            for line in fd_in.readlines():
                if "=======" in line:  # pylint: disable=no-else-continue
                    found_line = True
                    continue

                elif found_line:
                    title = line.strip()
                    break

        return title


def _create_tree(notes):
    """Transform a list of objects into a tree.

    :param notes: A list of Path() objects.
    :type notes: list: `Note`

    :return: Tree root node.
    :rtype: anytree.Node
    """
    nodes = {'root': anytree.Node('root')}

    for note in notes:
        parts = []

        for part in chain(['root'], note.parts[:-1]):
            parts.append(part)

            if '/'.join(parts) not in nodes:
                parent = nodes['/'.join(parts[:-1])]
                nodes['/'.join(parts)] = anytree.Node(part, parent=parent)

        anytree.Node(note,
                     parent=nodes['/'.join(parts)],
                     title=note.title,
                     ref_id=note.ref_id)

    return nodes['root']


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


def prune_tree(root, prune):
    """Prune nodes that shouldn't be rendered on the index page.

    :param root: Root node of the notes tree
    :type root: anytree.Node

    :param prune: An tuple of node names to be pruned
    :type prune: tuple

    :return: None
    """
    for node in anytree.search.findall(
            root, filter_=lambda node: node.name in prune):
        node.parent = None


def render_index(root, template, out):
    """Render notebook tree into index.rst.

    :param root: notebook tree root node
    :type root: class: anytree.Node

    :param template: A jinja2 template
    :type template: class: Jinja2.Template

    :param fd_out: Open file like object.
    :type fd_out: File Like Object

    :return: None
    """
    nodes = [node for node in anytree.PreOrderIter(root) if node.depth]
    out.write(template.render(nodes=nodes))


def render_note(template, out):
    """Render a note.

    :param template: A jinja2 template
    :type template: class: Jinja2.Template

    :param out: Open file like object.
    :type out: File Like Object

    :return: None
    """
    note_id = nanoid.generate(NANOID_ALPHABET, NANOID_SIZE)
    out.write(template.render(note_id=note_id))
