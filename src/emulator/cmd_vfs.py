"""Commands that change the VFS: mkdir, vfs-init, vfs-load."""

import posixpath

from emulator.cmd_utils import NO_ENTRY, split_flags
from emulator.errors import ShellError
from emulator.vfs import normalize
from emulator.vfs_loader import load_vfs


def make_dir(shell, path, parents):
    """Create one directory in memory, report errors like mkdir."""
    abs_path = normalize(path, shell.cwd)
    prefix = f"mkdir: cannot create directory '{path}':"
    existing = shell.vfs.find(abs_path)
    if existing is not None:
        if parents and existing.is_dir:
            return
        raise ShellError(f"{prefix} File exists")
    parent = shell.vfs.find(posixpath.dirname(abs_path))
    if parent is None and not parents:
        raise ShellError(f"{prefix} {NO_ENTRY}")
    if parent is not None and not parent.is_dir:
        raise ShellError(f"{prefix} Not a directory")
    try:
        shell.vfs.add_dir(abs_path)
    except NotADirectoryError as error:
        raise ShellError(f"{prefix} Not a directory") from error


def cmd_mkdir(shell, args):
    """Create directories in memory: mkdir [-p] dir..."""
    flags, paths = split_flags(args, "p", "mkdir")
    if not paths:
        raise ShellError("mkdir: missing operand")
    for path in paths:
        make_dir(shell, path, "p" in flags)
    return ""


def cmd_vfs_init(shell, args):
    """Replace the current VFS by the default one."""
    if args:
        raise ShellError("vfs-init: too many arguments")
    shell.reset_vfs()
    return ""


def cmd_vfs_load(shell, args):
    """Load a new VFS from a file on disk: vfs-load path."""
    if len(args) != 1:
        raise ShellError("usage: vfs-load path")
    vfs = load_vfs(args[0])
    shell.set_vfs(vfs, args[0])
    return ""
