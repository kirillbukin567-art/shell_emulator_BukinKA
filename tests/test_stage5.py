"""Tests of mkdir and vfs-load."""

import base64
import os
import tempfile
import unittest

from emulator.shell import Shell
from tests.helpers import make_shell, run
from tools.make_vfs import ARCHIVES, build_zip


class MkdirTest(unittest.TestCase):
    """The mkdir command."""

    def setUp(self):
        """Open the deep VFS."""
        self.shell = make_shell("deep")

    def test_create_and_list(self):
        """A new directory is visible and empty."""
        self.assertEqual(run(self.shell, "mkdir new"), "")
        self.assertIn("new", run(self.shell, "ls").split("\n"))
        self.assertEqual(run(self.shell, "ls new"), "")
        run(self.shell, "cd new")
        self.assertEqual(self.shell.cwd, "/new")

    def test_relative_to_cwd(self):
        """Paths are relative to the current directory."""
        run(self.shell, "cd /docs")
        run(self.shell, "mkdir fresh")
        self.assertIsNotNone(self.shell.vfs.find("/docs/fresh"))

    def test_several_operands(self):
        """Every operand is created."""
        run(self.shell, "mkdir a b")
        self.assertIsNotNone(self.shell.vfs.find("/a"))
        self.assertIsNotNone(self.shell.vfs.find("/b"))

    def test_parents_flag(self):
        """-p creates missing parents and accepts existing ones."""
        self.assertEqual(run(self.shell, "mkdir -p x/y/z"), "")
        self.assertIsNotNone(self.shell.vfs.find("/x/y/z"))
        self.assertEqual(run(self.shell, "mkdir -p x/y"), "")

    def test_errors(self):
        """Existing, missing parent, file parent and no operand fail."""
        self.assertIn("File exists", run(self.shell, "mkdir docs"))
        self.assertIn("File exists", run(self.shell, "mkdir readme.txt"))
        self.assertIn("No such file", run(self.shell, "mkdir p/q"))
        self.assertIn("Not a directory", run(self.shell, "mkdir readme.txt/q"))
        self.assertIn("Not a directory",
                      run(self.shell, "mkdir -p readme.txt/q/r"))
        self.assertIn("missing operand", run(self.shell, "mkdir"))
        self.assertIn("invalid option", run(self.shell, "mkdir -z a"))

    def test_changes_stay_in_memory(self):
        """The file the VFS was loaded from is not modified."""
        handle, path = tempfile.mkstemp(suffix=".b64")
        self.addCleanup(os.remove, path)
        text = base64.encodebytes(build_zip(ARCHIVES["files"]))
        with os.fdopen(handle, "wb") as stream:
            stream.write(text)
        shell = Shell(path)
        run(shell, "mkdir created")
        with open(path, "rb") as stream:
            self.assertEqual(stream.read(), text)
        run(shell, f"vfs-load {path}")
        self.assertNotIn("created", run(shell, "ls").split("\n"))


class VfsLoadTest(unittest.TestCase):
    """The vfs-load command."""

    def setUp(self):
        """Create a ZIP file on disk."""
        handle, self.path = tempfile.mkstemp(suffix=".zip")
        self.addCleanup(os.remove, self.path)
        with os.fdopen(handle, "wb") as stream:
            stream.write(build_zip({"d/f.txt": b"hello\n"}))

    def test_load_replaces_vfs(self):
        """The new VFS is active, the shell goes to its root."""
        shell = make_shell("deep")
        run(shell, "cd /docs")
        self.assertEqual(run(shell, f"vfs-load {self.path}"), "")
        self.assertEqual(shell.cwd, "/")
        self.assertEqual(run(shell, "tac d/f.txt"), "hello")
        self.assertEqual(shell.vfs_path, self.path)
        self.assertEqual(shell.prompt(), f"{shell.vfs.name}:/$ ")

    def test_failed_load_keeps_old_vfs(self):
        """A bad path or file leaves the current VFS untouched."""
        shell = make_shell("deep")
        self.assertIn("cannot read", run(shell, "vfs-load /no/such.zip"))
        self.assertIn("ERR", run(shell, f"vfs-load {__file__}"))
        self.assertEqual(shell.vfs.name, "deep")
        self.assertIn("docs", run(shell, "ls"))

    def test_usage(self):
        """Exactly one argument is needed."""
        shell = make_shell("deep")
        self.assertIn("usage", run(shell, "vfs-load"))
        self.assertIn("usage", run(shell, "vfs-load a b"))

    def test_init_after_load(self):
        """vfs-init returns to the default VFS."""
        shell = make_shell("deep")
        run(shell, f"vfs-load {self.path}")
        run(shell, "vfs-init")
        self.assertEqual(shell.vfs.name, "default")
        self.assertIsNone(shell.vfs_path)


if __name__ == "__main__":
    unittest.main()
