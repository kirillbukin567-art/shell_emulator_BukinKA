"""Helpers for the tests of commands."""

import base64
import os
import tempfile

from emulator.errors import ShellError
from emulator.shell import Shell
from tools.make_vfs import ARCHIVES, build_zip


def make_shell(archive="deep"):
    """Create a shell whose VFS is one of the demo archives."""
    handle, path = tempfile.mkstemp(suffix=".b64", prefix=archive + "-")
    with os.fdopen(handle, "wb") as stream:
        stream.write(base64.encodebytes(build_zip(ARCHIVES[archive])))
    try:
        shell = Shell(path)
    finally:
        os.remove(path)
    shell.vfs.name = archive
    return shell


def run(shell, line):
    """Execute a line; return the output, or 'ERR: message' on error."""
    try:
        return shell.execute(line)
    except ShellError as error:
        return f"ERR: {error}"
