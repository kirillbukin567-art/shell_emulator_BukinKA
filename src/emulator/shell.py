"""State of the emulated shell."""

from emulator.commands import run_command
from emulator.parser import parse_line

DEFAULT_VFS_NAME = "vfs"


class Shell:
    """Shell session: holds the state and executes command lines."""

    def __init__(self, vfs_name=DEFAULT_VFS_NAME, vfs_path=None):
        """Create a running shell with the given VFS name and location."""
        self.vfs_name = vfs_name
        self.vfs_path = vfs_path
        self.running = True

    def prompt(self):
        """Return the input prompt that contains the VFS name."""
        return f"{self.vfs_name}$ "

    def execute(self, line):
        """Execute one line and return its output (may raise ShellError)."""
        parsed = parse_line(line)
        if parsed is None:
            return ""
        name, args = parsed
        return run_command(self, name, args)
