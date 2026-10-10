"""State of the emulated shell."""

from emulator.commands import run_command
from emulator.parser import parse_line
from emulator.vfs import ROOT_PATH
from emulator.vfs_loader import default_vfs, load_vfs


class Shell:
    """Shell session: holds the state and executes command lines."""

    def __init__(self, vfs_path=None):
        """Create a running shell, load the VFS if a path is given."""
        self.running = True
        self.cwd = ROOT_PATH
        self.vfs_path = vfs_path
        self.vfs = load_vfs(vfs_path) if vfs_path else default_vfs()

    def prompt(self):
        """Return the input prompt that contains the VFS name."""
        return f"{self.vfs.name}:{self.cwd}$ "

    def reset_vfs(self):
        """Replace the VFS by the default one and forget its location."""
        self.vfs = default_vfs()
        self.vfs_path = None
        self.cwd = ROOT_PATH

    def execute(self, line):
        """Execute one line and return its output (may raise ShellError)."""
        parsed = parse_line(line)
        if parsed is None:
            return ""
        name, args = parsed
        return run_command(self, name, args)
