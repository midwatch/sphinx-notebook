"""Main module."""
import string
import dataclasses
from itertools import chain
from pathlib import Path
from typing import Dict
from typing import List

import anytree
import nanoid
import yaml

from . import util

NANOID_ALPHABET = '-0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
NANOID_SIZE = 10

@dataclasses.dataclass
class Note:
    root_dir: Path
    path: Path
    group: str = dataclasses.field(init=False)
    name: str = dataclasses.field(init=False)
    parents: List[str] = dataclasses.field(init=False)
    title: str = dataclasses.field(init=False)
    url: str = dataclasses.field(init=False)

    def __post_init__(self):
        target = self.path.relative_to(self.root_dir)

        self.group = util.parse_stem(self.path.stem)
        self.name = self.path.name
        self.parents = [util.to_title_case(x) for x in target.parts[:-1]]
        self.title = util.get_title(self.path)
        self.url = f'/{target.parent}/{target.stem}'


def get_notes(root_dir: Path, *, filter_: str ='_include' , note_pattern: str = '**/*.rst',
    meta_pattern: str ='**/*/_meta.yaml') -> (List[Note], Dict):
    """
    """
    notes = [Note(root_dir, x) for x in sorted(root_dir.glob(note_pattern)) if filter_ not in x.parts]

    meta_data = {}

    for meta_file in root_dir.glob(meta_pattern):
        node = util.to_title_case(str(meta_file.relative_to(root_dir).parent))

        with meta_file.open() as fd_in:
            payload = yaml.safe_load(fd_in)


        meta_data[node] = payload

    return (notes, meta_data)


def get_target():
    """Create a random target ID.

    :return: target id
    :rrtype: str
    """
    return nanoid.generate(NANOID_ALPHABET, NANOID_SIZE)



def to_tree(notes: List[Note], meta_data: Dict) -> anytree.Node:
    """Get a tree of notes from a list of notes and override meta data."""
    ROOT_NAME = "root"
    nodes = {ROOT_NAME: anytree.Node(ROOT_NAME)}
    resolver = anytree.resolver.Resolver()

    for note in notes:
        parts = []

        for part in chain([ROOT_NAME], note.parents):
            parts.append(part)

            if '/'.join(parts) not in nodes:
                parent = nodes['/'.join(parts[:-1])]
                nodes['/'.join(parts)] = anytree.Node(part, title=part, parent=parent)

        anytree.Node(note.name,
                     group = note.group,
                     parent = nodes['/'.join(parts)],
                     title = note.title,
                     url = note.url)

    for target, payload in meta_data.items():
        node = resolver.get(nodes[ROOT_NAME], f'/{ROOT_NAME}/{target}')
        node.title = payload['title']

    return nodes[ROOT_NAME]


def render_index(root, title, header, template, out):
    """Render notebook tree into index.rst.

    :param root: notebook tree root node
    :type root: class: anytree.Node

    :param template: A jinja2 template
    :type template: class: Jinja2.Template

    :param fd_out: Open file like object.
    :type fd_out: File Like Object

    :return: None
    """
    ctx = {
        'title': title,
        'header': header,
        'nodes': [node for node in anytree.PreOrderIter(root) if node.depth]
    }

    out.write(template.render(ctx))


def render_note(template, out):
    """Render a note.

    :param template: A jinja2 template
    :type template: class: Jinja2.Template

    :param out: Open file like object.
    :type out: File Like Object

    :return: None
    """
    note_id = get_target()
    out.write(template.render(note_id=note_id))
