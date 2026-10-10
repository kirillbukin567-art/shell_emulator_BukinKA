"""Navigation commands: ls, cd, pwd."""

import posixpath

from emulator.cmd_utils import NO_ENTRY, lookup, split_flags
from emulator.errors import ShellError
from emulator.vfs import ROOT_PATH

DIR_MODE = "drwxr-xr-x"
FILE_MODE = "-rw-r--r--"
SIZE_WIDTH = 8


def visible_names(node, show_all):
    """Return sorted names of children; dot files need the -a flag."""
    names = sorted(node.children)
    if show_all:
        return [".", ".."] + names
    return [name for name in names if not name.startswith(".")]


def long_line(name, node):
    """Format one line of the 'ls -l' listing."""
    mode = DIR_MODE if node.is_dir else FILE_MODE
    size = 0 if node.is_dir else len(node.data)
    return f"{mode} {size:>{SIZE_WIDTH}} {name}"


def entry_lines(node, parent, flags):
    """Return output lines for the entries of one directory."""
    lines = []
    for name in visible_names(node, "a" in flags):
        if name == ".":
            child = node
        elif name == "..":
            child = parent
        else:
            child = node.children[name]
        lines.append(long_line(name, child) if "l" in flags else name)
    return lines


def list_one(shell, path, flags):
    """List a directory, or show a single file as ls does."""
    abs_path, node = lookup_for_ls(shell, path)
    if not node.is_dir:
        return [long_line(path, node) if "l" in flags else path]
    parent = shell.vfs.find(posixpath.dirname(abs_path))
    return entry_lines(node, parent, flags)


def lookup_for_ls(shell, path):
    """Find a node, report a missing one in the style of ls."""
    try:
        return lookup(shell, "ls", path)
    except ShellError as error:
        raise ShellError(
            f"ls: cannot access '{path}': {NO_ENTRY}") from error


def cmd_ls(shell, args):
    """List directory contents: ls [-l] [-a] [path...]."""
    flags, paths = split_flags(args, "la", "ls")
    paths = paths or ["."]
    blocks = []
    for path in paths:
        lines = list_one(shell, path, flags)
        if len(paths) > 1:
            lines.insert(0, f"{path}:")
        blocks.append("\n".join(lines))
    return "\n\n".join(block for block in blocks if block)


def cmd_cd(shell, args):
    """Change the current directory: cd [path]."""
    if len(args) > 1:
        raise ShellError("cd: too many arguments")
    target = args[0] if args else ROOT_PATH
    abs_path, node = lookup(shell, "cd", target)
    if not node.is_dir:
        raise ShellError(f"cd: {target}: Not a directory")
    shell.cwd = abs_path
    return ""


def cmd_pwd(shell, args):
    """Print the current directory."""
    if args:
        raise ShellError("pwd: too many arguments")
    return shell.cwd
