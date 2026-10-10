"""Tests of the command line parser."""

import unittest

from emulator.errors import ShellError
from emulator.parser import expand_vars, parse_line, split_line

ENV = {"HOME": "/home/user", "NAME": "abc"}


class ParserTest(unittest.TestCase):
    """Parsing of command lines."""

    def test_empty_line(self):
        """Empty and blank lines give nothing."""
        self.assertIsNone(parse_line(""))
        self.assertIsNone(parse_line("   \t "))

    def test_command_and_args(self):
        """The first word is the command, the rest are arguments."""
        self.assertEqual(parse_line("ls -l /a"), ("ls", ["-l", "/a"]))

    def test_expand_variables(self):
        """Both $NAME and ${NAME} forms are expanded."""
        self.assertEqual(expand_vars("$HOME/x", ENV), "/home/user/x")
        self.assertEqual(expand_vars("${NAME}d", ENV), "abcd")

    def test_unknown_variable_is_empty(self):
        """An unset variable expands to an empty string."""
        self.assertEqual(expand_vars("a$NOPE.b", ENV), "a.b")

    def test_lonely_dollar_is_kept(self):
        """A dollar sign without a name stays as it is."""
        self.assertEqual(expand_vars("cost $ 5", ENV), "cost $ 5")

    def test_quotes(self):
        """Double quotes expand variables, single quotes do not."""
        self.assertEqual(split_line('a "b $NAME" c', ENV), ["a", "b abc", "c"])
        self.assertEqual(split_line("a '$NAME'", ENV), ["a", "$NAME"])

    def test_empty_quoted_word(self):
        """An empty quoted string is still a word."""
        self.assertEqual(split_line("a '' b", ENV), ["a", "", "b"])

    def test_glued_segments(self):
        """Quoted and bare parts without spaces form a single word."""
        self.assertEqual(split_line("x'a b'\"$NAME\"", ENV), ["xa babc"])

    def test_unterminated_quote(self):
        """An unclosed quote is a syntax error."""
        with self.assertRaises(ShellError):
            split_line("echo 'oops")


if __name__ == "__main__":
    unittest.main()
