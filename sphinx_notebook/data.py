"""Data classes."""
import dataclasses
from typing import List

import anytree
import yaml

from . import util


@dataclasses.dataclass
class MetaData:
    """Meta data overrides for sections."""

    path: str
    header: str = dataclasses.field(default='')
    title: str = dataclasses.field(default=None)

    @classmethod
    def from_yaml(cls, root_dir, path):
        """Create a MetaData class from a meta data file."""
        meta_data = {'path': str(path.relative_to(root_dir).parent)}
        with path.open() as fd_in:
            meta_data.update(yaml.safe_load(fd_in))

        return cls(**meta_data)

    def to_dict(self):
        """Return meta data as dict."""
        data = {'header': self.header}

        if self.title:
            data['title'] = self.title

        return data


class Node(anytree.Node):
    """Class representing a note."""

    def __eq__(self, other):
        """Compare Nodes on name attribute."""
        return self.name == other.name

    def _recursive_parents(self, parents):
        if parents:
            yield parents[0]
            yield from self._recursive_parents(parents[1:])

    def add_parents(self, parents):
        """Add parent nodes."""
        for parent in parents:
            try:
                child = self.children[self.children.index(Node(parent))]

            except ValueError:
                child = Node(parent, self, title=util.to_title_case(parent))

            child.add_parents(parents)

    def add_note(self, note):
        """Add a note to notebook tree."""
        resolver = anytree.resolver.Resolver()

        self.add_parents(self._recursive_parents(note.parents))

        Node(note.name,
             group=note.group,
             parent=resolver.get(self, note.parent_path),
             title=note.title,
             url=note.url)

    def update(self, meta_data):
        """Update members using meta data overrides."""
        for key, value in meta_data.items():
            setattr(self, key, value)


@dataclasses.dataclass
class Note:
    """A note from the notebook tree."""

    group: str
    name: str
    parents: List[str]
    title: str
    url: str

    @classmethod
    def from_path(cls, root_dir, path):
        """Create a node class from a Path() object."""
        target = path.relative_to(root_dir)

        group = util.parse_stem(path.stem)
        name = path.name
        parents = list(target.parts[:-1])
        title = util.get_title(path)
        url = f'/{target.parent}/{target.stem}'

        return cls(group, name, parents, title, url)

    @property
    def parent_path(self):
        """Return a relative path of note."""
        return '/'.join(self.parents)
