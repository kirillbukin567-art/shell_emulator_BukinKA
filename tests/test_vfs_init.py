"""Tests of the vfs-init command."""

import unittest

from emulator.errors import ShellError
from emulator.shell import Shell


class VfsInitTest(unittest.TestCase):
    """Reset to the default VFS."""

    def test_replaces_vfs_and_forgets_location(self):
        """After vfs-init the default VFS is active, location is cleared."""
        shell = Shell("vfs/files.b64")
        self.assertEqual(shell.vfs.name, "files")
        shell.execute("vfs-init")
        self.assertEqual(shell.vfs.name, "default")
        self.assertIsNone(shell.vfs_path)
        self.assertEqual(shell.cwd, "/")

    def test_arguments_are_rejected(self):
        """The command takes no arguments."""
        with self.assertRaises(ShellError):
            Shell().execute("vfs-init now")


if __name__ == "__main__":
    unittest.main()
