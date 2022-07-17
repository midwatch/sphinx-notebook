"""Main module."""
import dataclasses
from itertools import chain
from pathlib import Path
from typing import IO, Dict, List

import anytree
import jinja2
import nanoid
import yaml

from . import util

NANOID_ALPHABET = '-0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
NANOID_SIZE = 10


@dataclasses.dataclass
class MetaData:
    """Meta data overrides for sections."""

    title: str
    name: str
    header: str = dataclasses.field(default='')

    @classmethod
    def from_yaml(cls, root_dir, path):
        """Create a MetaData class from a meta data file."""
        with path.open() as fd_in:
            payload = yaml.safe_load(fd_in)

        payload['name'] = util.to_title_case(
            str(path.relative_to(root_dir).parent))
        return cls(**payload)


@dataclasses.dataclass
class Note:
    """A note from the notebook tree."""

    root_dir: Path
    path: Path
    group: str = dataclasses.field(init=False)
    name: str = dataclasses.field(init=False)
    parents: List[str] = dataclasses.field(init=False)
    title: str = dataclasses.field(init=False)
    url: str = dataclasses.field(init=False)

    def __post_init__(self):
        """Initialize dependant fields."""
        target = self.path.relative_to(self.root_dir)

        self.group = util.parse_stem(self.path.stem)
        self.name = self.path.name
        self.parents = [util.to_title_case(x) for x in target.parts[:-1]]
        self.title = util.get_title(self.path)
        self.url = f'/{target.parent}/{target.stem}'


def get_notes(
        root_dir: Path,
        *,
        filter_: str = '_include',
        note_pattern: str = '**/*.rst',
        meta_pattern: str = '**/_meta.yaml') -> (List[Note], List[MetaData]):
    """Return notes and meta data from notebook."""
    notes = [
        Note(root_dir, x) for x in sorted(root_dir.glob(note_pattern))
        if filter_ not in x.parts
    ]

    meta_data = [
        MetaData.from_yaml(root_dir, x) for x in root_dir.glob(meta_pattern)
    ]

    return (notes, meta_data)


def get_target() -> str:
    """Create a random target ID."""
    return nanoid.generate(NANOID_ALPHABET, NANOID_SIZE)


def to_tree(notes: List[Note], meta_data: Dict) -> anytree.Node:
    """Get a tree of notes from a list of notes and override meta data."""
    root_name = "root"
    nodes = {root_name: anytree.Node(root_name)}
    resolver = anytree.resolver.Resolver()

    for note in notes:
        parts = []

        for part in chain([root_name], note.parents):
            parts.append(part)

            if '/'.join(parts) not in nodes:
                parent = nodes['/'.join(parts[:-1])]
                nodes['/'.join(parts)] = anytree.Node(part,
                                                      title=part,
                                                      parent=parent)

        anytree.Node(note.name,
                     group=note.group,
                     parent=nodes['/'.join(parts)],
                     title=note.title,
                     url=note.url)

    for meta in meta_data:
        node = resolver.get(nodes[root_name], f'/{root_name}/{meta.name}')
        node.title = meta.title

    return nodes[root_name]


def render_index(root: anytree.Node, title: str, header: str,
                 template: jinja2.Template, out: IO[str]) -> None:
    """Render notebook tree into index.rst."""
    ctx = {
        'title': title,
        'header': header,
        'nodes': [node for node in anytree.PreOrderIter(root) if node.depth]
    }

    out.write(template.render(ctx))


def render_note(template: jinja2.Template, out: IO[str]) -> None:
    """Render a single note for export."""
    note_id = get_target()
    out.write(template.render(note_id=note_id))
