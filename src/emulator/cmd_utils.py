"""Helpers shared by the commands."""

from emulator.errors import ShellError
from emulator.vfs import normalize

NO_ENTRY = "No such file or directory"


def split_flags(args, allowed, command):
    """Split arguments into a set of one-letter flags and operands."""
    flags = set()
    operands = []
    options_done = False
    for arg in args:
        if options_done or arg == "-" or not arg.startswith("-"):
            operands.append(arg)
        elif arg == "--":
            options_done = True
        else:
            flags.update(check_letters(arg[1:], allowed, command))
    return flags, operands


def check_letters(letters, allowed, command):
    """Return the letters of a flag group, reject unknown ones."""
    for letter in letters:
        if letter not in allowed:
            raise ShellError(f"{command}: invalid option -- '{letter}'")
    return set(letters)


def lookup(shell, command, path):
    """Return (absolute path, node) or raise a 'no such file' error."""
    abs_path = normalize(path, shell.cwd)
    node = shell.vfs.find(abs_path)
    if node is None:
        raise ShellError(f"{command}: {path}: {NO_ENTRY}")
    return abs_path, node


def read_text_file(shell, command, path):
    """Return the lines of a file in the VFS."""
    _, node = lookup(shell, command, path)
    if node.is_dir:
        raise ShellError(f"{command}: {path}: read error: Is a directory")
    return node.data.decode("utf-8", errors="replace").splitlines()
