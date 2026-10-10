"""Tests of the interactive loop."""

import unittest

from emulator.repl import run_repl
from emulator.shell import Shell


def run_session(lines):
    """Feed lines to the REPL, return (prompts, output)."""
    feed = iter(lines)
    prompts = []
    output = []

    def fake_input(prompt):
        """Return the next prepared line or signal end of input."""
        prompts.append(prompt)
        try:
            return next(feed)
        except StopIteration:
            raise EOFError from None

    run_repl(Shell(), fake_input, output.append)
    return prompts, output


class ReplTest(unittest.TestCase):
    """Behaviour of the dialog with the user."""

    def test_prompt_has_vfs_name(self):
        """The prompt contains the VFS name."""
        prompts, _ = run_session(["exit"])
        self.assertIn("vfs", prompts[0])

    def test_stubs_print_name_and_args(self):
        """Stub commands echo their name and arguments."""
        _, output = run_session(["ls -l /a", "cd /b", "exit"])
        self.assertEqual(output, ["ls -l /a", "cd /b"])

    def test_unknown_command_is_reported(self):
        """Unknown commands print an error and the loop goes on."""
        _, output = run_session(["nope", "exit"])
        self.assertEqual(output, ["error: nope: command not found"])

    def test_syntax_error_is_reported(self):
        """A parse error does not stop the shell."""
        _, output = run_session(["ls 'x", "ls ok", "exit"])
        self.assertEqual(len(output), 2)
        self.assertTrue(output[0].startswith("error:"))

    def test_exit_stops_loop(self):
        """Nothing after exit is read."""
        prompts, _ = run_session(["exit", "ls"])
        self.assertEqual(len(prompts), 1)

    def test_eof_stops_loop(self):
        """End of input leaves the shell gracefully."""
        prompts, _ = run_session([])
        self.assertEqual(len(prompts), 1)


if __name__ == "__main__":
    unittest.main()
