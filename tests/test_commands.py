"""Tests of ls, cd, pwd, tac, tail and find."""

import unittest

from tests.helpers import make_shell, run


class LsTest(unittest.TestCase):
    """The ls command."""

    def setUp(self):
        """Open the deep VFS."""
        self.shell = make_shell("deep")

    def test_root_listing(self):
        """The root is listed in sorted order."""
        out = run(self.shell, "ls").split("\n")
        self.assertEqual(out, ["bin", "docs", "empty_dir", "readme.txt",
                               "src"])

    def test_long_format(self):
        """-l shows type, size and name."""
        out = run(self.shell, "ls -l /docs/api/v1")
        self.assertIn("-rw-r--r--", out)
        self.assertTrue(out.splitlines()[0].endswith("notes.md"))
        self.assertIn("drwxr-xr-x", run(self.shell, "ls -l /"))

    def test_all_shows_dots(self):
        """-a adds . and .."""
        out = run(self.shell, "ls -a /empty_dir").split("\n")
        self.assertEqual(out, [".", ".."])

    def test_file_and_many_paths(self):
        """A file is printed by name; several paths get headers."""
        self.assertEqual(run(self.shell, "ls readme.txt"), "readme.txt")
        out = run(self.shell, "ls /docs /src")
        self.assertIn("/docs:\napi\nguide.txt", out)
        self.assertIn("\n\n/src:\nlib\nmain.py", out)

    def test_errors(self):
        """Missing path and bad option are reported."""
        self.assertEqual(
            run(self.shell, "ls /nope"),
            "ERR: ls: cannot access '/nope': No such file or directory")
        self.assertIn("invalid option", run(self.shell, "ls -z"))

    def test_relative_after_cd(self):
        """Relative paths use the current directory."""
        run(self.shell, "cd docs/api")
        self.assertEqual(run(self.shell, "ls"), "v1\nv2")
        self.assertEqual(run(self.shell, "ls ../.."), run(self.shell, "ls /"))


class CdTest(unittest.TestCase):
    """The cd and pwd commands."""

    def setUp(self):
        """Open the deep VFS."""
        self.shell = make_shell("deep")

    def test_cd_changes_prompt(self):
        """The prompt shows the new directory."""
        run(self.shell, "cd /docs/api/v1")
        self.assertEqual(self.shell.prompt(), "deep:/docs/api/v1$ ")
        self.assertEqual(run(self.shell, "pwd"), "/docs/api/v1")

    def test_cd_dotdot_and_home(self):
        """.. goes up, no argument goes to the root."""
        run(self.shell, "cd /docs/api")
        run(self.shell, "cd ..")
        self.assertEqual(self.shell.cwd, "/docs")
        run(self.shell, "cd")
        self.assertEqual(self.shell.cwd, "/")
        run(self.shell, "cd ../../..")
        self.assertEqual(self.shell.cwd, "/")

    def test_cd_errors(self):
        """Missing, non-directory and extra arguments are errors."""
        self.assertIn("No such file", run(self.shell, "cd /nope"))
        self.assertIn("Not a directory", run(self.shell, "cd readme.txt"))
        self.assertIn("too many", run(self.shell, "cd a b"))
        self.assertEqual(self.shell.cwd, "/")


class TacTailTest(unittest.TestCase):
    """The tac and tail commands."""

    def setUp(self):
        """Open the VFS with several files."""
        self.shell = make_shell("files")

    def test_tac(self):
        """Lines come in reverse order."""
        self.assertEqual(run(self.shell, "tac a.txt"), "gamma\nbeta\nalpha")

    def test_tac_many_files_and_empty(self):
        """Every file is reversed on its own, in the given order."""
        self.assertEqual(run(self.shell, "tac b.txt a.txt empty.txt"),
                         "two\none\ngamma\nbeta\nalpha")

    def test_tac_errors(self):
        """No operand, missing file and directory are errors."""
        self.assertIn("missing file operand", run(self.shell, "tac"))
        self.assertIn("No such file", run(self.shell, "tac nope"))
        self.assertIn("Is a directory", run(self.shell, "tac /"))

    def test_tail_default_is_ten(self):
        """Without options the last ten lines are shown."""
        out = run(self.shell, "tail log.txt").split("\n")
        self.assertEqual(out[0], "line 6")
        self.assertEqual(out[-1], "line 15")
        self.assertEqual(len(out), 10)

    def test_tail_n_forms(self):
        """-n N, -nN and -N are accepted."""
        for form in ("tail -n 2 log.txt", "tail -n2 log.txt",
                     "tail -2 log.txt"):
            self.assertEqual(run(self.shell, form), "line 14\nline 15")

    def test_tail_short_file_and_zero(self):
        """A short file is printed whole; -n 0 prints nothing."""
        self.assertEqual(run(self.shell, "tail b.txt"), "one\ntwo")
        self.assertEqual(run(self.shell, "tail -n 0 b.txt"), "")

    def test_tail_headers(self):
        """With several files each block has a header."""
        out = run(self.shell, "tail -n 1 a.txt b.txt")
        self.assertEqual(out, "==> a.txt <==\ngamma\n\n==> b.txt <==\ntwo")

    def test_tail_errors(self):
        """Bad count, missing operand and missing file are errors."""
        self.assertIn("invalid number", run(self.shell, "tail -n x a.txt"))
        self.assertIn("requires an argument", run(self.shell, "tail -n"))
        self.assertIn("missing file operand", run(self.shell, "tail"))
        self.assertIn("No such file", run(self.shell, "tail nope"))
        self.assertIn("invalid option", run(self.shell, "tail -z a.txt"))

    def test_unicode_and_binary(self):
        """UTF-8 text works; binary data does not crash."""
        self.assertEqual(run(self.shell, "tac unicode.txt"), "мир\nпривет")
        deep = make_shell("deep")
        self.assertIsInstance(run(deep, "tac bin/data.bin"), str)


class FindTest(unittest.TestCase):
    """The find command."""

    def setUp(self):
        """Open the deep VFS."""
        self.shell = make_shell("deep")

    def test_default_start(self):
        """Without a path find starts from the current directory."""
        run(self.shell, "cd /docs/api/v1")
        self.assertEqual(run(self.shell, "find"),
                         ".\n./notes.md\n./spec.txt")

    def test_name(self):
        """-name accepts glob patterns."""
        out = run(self.shell, "find / -name 'spec*'").split("\n")
        self.assertEqual(out, ["/docs/api/v1/spec.txt",
                               "/docs/api/v2/spec.txt"])

    def test_type(self):
        """-type separates files and directories."""
        dirs = run(self.shell, "find /docs -type d").split("\n")
        self.assertEqual(dirs, ["/docs", "/docs/api", "/docs/api/v1",
                                "/docs/api/v2"])
        files = run(self.shell, "find /src -type f -name '*.py'")
        self.assertEqual(files.count("\n"), 1)

    def test_start_is_shown_as_written(self):
        """Relative starts give relative results."""
        self.assertEqual(run(self.shell, "find docs/api/v2"),
                         "docs/api/v2\ndocs/api/v2/spec.txt")

    def test_no_match_is_empty(self):
        """Nothing found gives an empty output."""
        self.assertEqual(run(self.shell, "find / -name zzz"), "")

    def test_errors(self):
        """Missing path and bad expressions are errors."""
        self.assertIn("No such file", run(self.shell, "find /nope"))
        self.assertIn("unknown predicate", run(self.shell, "find / -foo x"))
        self.assertIn("missing argument", run(self.shell, "find / -name"))
        self.assertIn("-type", run(self.shell, "find / -type q"))


if __name__ == "__main__":
    unittest.main()
