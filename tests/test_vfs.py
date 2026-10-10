"""Tests of the VFS and its loading."""

import base64
import io
import os
import tempfile
import unittest
import zipfile

from emulator.errors import ShellError
from emulator.vfs import Vfs, normalize
from emulator.vfs_loader import (default_vfs, load_vfs, unwrap_container,
                                 vfs_from_bytes)
from tools.make_vfs import ARCHIVES, build_zip


class NormalizeTest(unittest.TestCase):
    """Normalization of paths."""

    def test_absolute_and_relative(self):
        """Relative paths are joined with the current directory."""
        self.assertEqual(normalize("/a//b/"), "/a/b")
        self.assertEqual(normalize("c", "/a/b"), "/a/b/c")
        self.assertEqual(normalize("../x", "/a/b"), "/a/x")

    def test_cannot_leave_root(self):
        """Going above the root stays in the root."""
        self.assertEqual(normalize("/../../a"), "/a")
        self.assertEqual(normalize("..", "/"), "/")


class VfsTest(unittest.TestCase):
    """Operations on the tree."""

    def test_add_and_find(self):
        """A file creates its parent directories."""
        vfs = Vfs("t")
        vfs.add_file("/a/b/c.txt", b"x")
        self.assertTrue(vfs.find("/a/b").is_dir)
        self.assertEqual(vfs.find("/a/b/c.txt").data, b"x")
        self.assertIsNone(vfs.find("/a/zzz"))
        self.assertIsNone(vfs.find("/a/b/c.txt/d"))

    def test_file_blocks_directory(self):
        """A directory cannot be created below a file."""
        vfs = Vfs()
        vfs.add_file("/a", b"")
        with self.assertRaises(NotADirectoryError):
            vfs.add_dir("/a/b")

    def test_walk_is_sorted(self):
        """Walking gives sorted paths, the start node first."""
        vfs = Vfs()
        vfs.add_file("/b", b"")
        vfs.add_file("/a/z", b"")
        paths = [path for path, _ in vfs.walk("/")]
        self.assertEqual(paths, ["/", "/a", "/a/z", "/b"])


class LoaderTest(unittest.TestCase):
    """Creation of VFS objects."""

    def test_default(self):
        """The default VFS has files and a name."""
        vfs = default_vfs()
        self.assertEqual(vfs.name, "default")
        self.assertIsNotNone(vfs.find("/docs/notes.txt"))

    def test_zip_and_base64_are_equal(self):
        """Raw ZIP and its base64 text give the same tree."""
        raw = build_zip(ARCHIVES["deep"])
        text = base64.encodebytes(raw)
        first = vfs_from_bytes(raw, "a")
        second = vfs_from_bytes(text, "b")
        self.assertEqual([p for p, _ in first.walk("/")],
                         [p for p, _ in second.walk("/")])

    def test_binary_data_survives(self):
        """Binary files keep every byte."""
        vfs = vfs_from_bytes(build_zip(ARCHIVES["deep"]), "d")
        self.assertEqual(vfs.find("/bin/data.bin").data, bytes(range(256)))

    def test_three_levels_and_empty_dir(self):
        """The deep archive has 3+ levels and an empty directory."""
        vfs = vfs_from_bytes(build_zip(ARCHIVES["deep"]), "d")
        self.assertIsNotNone(vfs.find("/docs/api/v1/spec.txt"))
        self.assertTrue(vfs.find("/empty_dir").is_dir)

    def test_unsafe_names_stay_inside(self):
        """Entries with '..' cannot escape the root."""
        vfs = vfs_from_bytes(build_zip({"../../evil.txt": b"x"}), "e")
        self.assertIsNotNone(vfs.find("/evil.txt"))

    def test_garbage_is_rejected(self):
        """Random data and bad base64 raise a shell error."""
        with self.assertRaises(ShellError):
            unwrap_container(b"definitely not a zip")
        with self.assertRaises(ShellError):
            unwrap_container(base64.b64encode(b"plain text"))

    def test_load_from_disk(self):
        """The VFS name is the file name without extension."""
        handle, path = tempfile.mkstemp(suffix=".zip")
        self.addCleanup(os.remove, path)
        with os.fdopen(handle, "wb") as stream:
            stream.write(build_zip({"x.txt": b"1"}))
        vfs = load_vfs(path)
        self.assertEqual(vfs.name, os.path.basename(path)[:-4])
        self.assertEqual(vfs.find("/x.txt").data, b"1")

    def test_missing_file(self):
        """A missing file is a shell error, not a crash."""
        with self.assertRaises(ShellError):
            load_vfs("/no/such/vfs.zip")

    def test_nothing_is_written_to_disk(self):
        """Loading does not create files next to the process."""
        before = set(os.listdir("."))
        vfs_from_bytes(build_zip(ARCHIVES["files"]), "f")
        self.assertEqual(set(os.listdir(".")), before)

    def test_zip_helper_is_valid(self):
        """The generated archives are real ZIP files."""
        for entries in ARCHIVES.values():
            raw = build_zip(entries)
            self.assertTrue(zipfile.is_zipfile(io.BytesIO(raw)))


if __name__ == "__main__":
    unittest.main()
