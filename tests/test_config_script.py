"""Tests of configuration and startup scripts."""

import os
import tempfile
import unittest

from emulator.config import format_debug, parse_config
from emulator.errors import ShellError
from emulator.script import run_script
from emulator.shell import Shell


def write_temp(text):
    """Write text into a temporary file and return its path."""
    handle, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(handle, "w", encoding="utf-8") as stream:
        stream.write(text)
    return path


class ConfigTest(unittest.TestCase):
    """Command line parameters."""

    def test_defaults(self):
        """Without arguments both parameters are empty."""
        config = parse_config([])
        self.assertIsNone(config.vfs_path)
        self.assertIsNone(config.script_path)

    def test_both_parameters(self):
        """Both parameters are read."""
        config = parse_config(["--vfs", "a.zip", "--script", "s.txt"])
        self.assertEqual((config.vfs_path, config.script_path),
                         ("a.zip", "s.txt"))

    def test_debug_output_shows_parameters(self):
        """Debug output lists every parameter."""
        text = "\n".join(format_debug(parse_config(["--vfs", "a.zip"])))
        self.assertIn("a.zip", text)
        self.assertIn("script", text)


class ScriptTest(unittest.TestCase):
    """Execution of startup scripts."""

    def run_text(self, text):
        """Run a script text and return (failed, output)."""
        path = write_temp(text)
        self.addCleanup(os.remove, path)
        output = []
        failed = run_script(Shell(), path, output.append)
        return failed, output

    def test_input_and_output_are_shown(self):
        """The prompt with the command is printed before its output."""
        failed, output = self.run_text("ls a\n")
        self.assertEqual(failed, 0)
        self.assertEqual(output, ["vfs$ ls a", "ls a"])

    def test_errors_are_skipped(self):
        """A failed line is counted and the script continues."""
        failed, output = self.run_text("bad\nls ok\n")
        self.assertEqual(failed, 1)
        self.assertEqual(output[-1], "ls ok")

    def test_comments_and_blank_lines(self):
        """Comments and blank lines are not executed or shown."""
        _, output = self.run_text("# note\n\nls\n")
        self.assertEqual(output, ["vfs$ ls", "ls"])

    def test_exit_stops_script(self):
        """Lines after exit are not executed."""
        _, output = self.run_text("exit\nls\n")
        self.assertEqual(output, ["vfs$ exit"])

    def test_missing_script(self):
        """A missing file raises a shell error."""
        with self.assertRaises(ShellError):
            run_script(Shell(), "/no/such/script.txt")


if __name__ == "__main__":
    unittest.main()
