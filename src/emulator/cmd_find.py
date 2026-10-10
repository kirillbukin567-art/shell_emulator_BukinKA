"""The find command: find [path...] [-name PATTERN] [-type f|d]."""

import fnmatch
import posixpath

from emulator.cmd_utils import NO_ENTRY, lookup
from emulator.errors import ShellError

TYPES = {"f": False, "d": True}


def make_name_test(pattern):
    """Return a test that matches the base name with a glob pattern."""
    def test(name, node):
        """Check the name of a node."""
        return fnmatch.fnmatchcase(name, pattern)
    return test


def make_type_test(kind):
    """Return a test for the type of a node: f (file) or d (dir)."""
    if kind not in TYPES:
        raise ShellError(f"find: unknown argument to -type: {kind}")

    def test(name, node):
        """Check the type of a node."""
        return node.is_dir == TYPES[kind]
    return test


def split_expression(args):
    """Return (start paths, expression arguments)."""
    for index, arg in enumerate(args):
        if arg.startswith("-"):
            return args[:index], args[index:]
    return list(args), []


def parse_tests(expression):
    """Turn expression arguments into a list of test functions."""
    makers = {"-name": make_name_test, "-type": make_type_test}
    tests = []
    index = 0
    while index < len(expression):
        option = expression[index]
        if option not in makers:
            raise ShellError(f"find: unknown predicate '{option}'")
        if index + 1 >= len(expression):
            raise ShellError(f"find: missing argument to '{option}'")
        tests.append(makers[option](expression[index + 1]))
        index += 2
    return tests


def display_path(start, start_abs, abs_path):
    """Show a found path relative to the way the user wrote the start."""
    relative = posixpath.relpath(abs_path, start_abs)
    return start if relative == "." else posixpath.join(start, relative)


def node_name(abs_path, node):
    """Name used by -name; the root is called '/'."""
    return node.name or posixpath.basename(abs_path) or "/"


def find_from(shell, start, tests):
    """Return the matching paths below one start path."""
    try:
        start_abs, _ = lookup(shell, "find", start)
    except ShellError as error:
        raise ShellError(f"find: '{start}': {NO_ENTRY}") from error
    found = []
    for abs_path, node in shell.vfs.walk(start_abs):
        name = node_name(abs_path, node)
        if all(test(name, node) for test in tests):
            found.append(display_path(start, start_abs, abs_path))
    return found


def cmd_find(shell, args):
    """Search for files: find [path...] [-name PATTERN] [-type f|d]."""
    starts, expression = split_expression(args)
    tests = parse_tests(expression)
    found = []
    for start in starts or ["."]:
        found.extend(find_from(shell, start, tests))
    return "\n".join(found)
