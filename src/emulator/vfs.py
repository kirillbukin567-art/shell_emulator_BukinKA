"""Virtual file system that lives completely in memory."""

import posixpath
from dataclasses import dataclass, field

ROOT_PATH = "/"
DEFAULT_VFS_NAME = "default"


@dataclass
class Node:
    """File or directory of the VFS."""

    name: str
    is_dir: bool
    children: dict = field(default_factory=dict)
    data: bytes = b""


def split_path(path):
    """Return the non-empty components of an absolute path."""
    return [part for part in path.split("/") if part]


def normalize(path, cwd=ROOT_PATH):
    """Make an absolute normalized path; '..' above the root is ignored."""
    full = path if path.startswith("/") else posixpath.join(cwd, path)
    return posixpath.normpath("/" + full.lstrip("/"))


class Vfs:
    """Tree of nodes with a name (shown in the prompt)."""

    def __init__(self, name=DEFAULT_VFS_NAME):
        """Create an empty VFS that has only the root directory."""
        self.name = name
        self.root = Node("", True)

    def find(self, abs_path):
        """Return the node by absolute path or None."""
        node = self.root
        for part in split_path(abs_path):
            if not node.is_dir or part not in node.children:
                return None
            node = node.children[part]
        return node

    def add_dir(self, abs_path):
        """Create a directory and all missing parents."""
        node = self.root
        for part in split_path(abs_path):
            child = node.children.get(part)
            if child is None:
                child = Node(part, True)
                node.children[part] = child
            elif not child.is_dir:
                raise NotADirectoryError(abs_path)
            node = child
        return node

    def add_file(self, abs_path, data):
        """Create a file with data; missing directories are created."""
        parent_path, name = posixpath.split(normalize(abs_path))
        if not name:
            raise IsADirectoryError(abs_path)
        parent = self.add_dir(parent_path)
        parent.children[name] = Node(name, False, data=bytes(data))

    def walk(self, abs_path):
        """Yield (path, node) for a node and everything below it."""
        start = self.find(abs_path)
        if start is None:
            return
        yield from self.walk_node(normalize(abs_path), start)

    def walk_node(self, path, node):
        """Yield (path, node) depth first, children sorted by name."""
        yield path, node
        for name in sorted(node.children):
            child_path = posixpath.join(path, name)
            yield from self.walk_node(child_path, node.children[name])
