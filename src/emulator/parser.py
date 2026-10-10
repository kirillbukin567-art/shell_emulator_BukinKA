"""Command line parser with environment variable expansion."""

import os
import re

from emulator.errors import ShellError

VAR_PATTERN = re.compile(r"\$(?:\{(\w+)\}|(\w+))")
SEGMENT_PATTERN = re.compile(r"""'([^']*)'|"([^"]*)"|([^\s'"]+)""")


def expand_vars(text, env=None):
    """Replace $NAME and ${NAME} with values from the environment."""
    source = os.environ if env is None else env

    def replace(match):
        """Return the value of the variable found by the match."""
        name = match.group(1) or match.group(2)
        return source.get(name, "")

    return VAR_PATTERN.sub(replace, text)


def convert_segment(match, env):
    """Turn one quoted or bare fragment of a word into plain text."""
    single, double, bare = match.groups()
    if single is not None:
        return single
    text = double if double is not None else bare
    return expand_vars(text, env)


def read_word(line, pos, env):
    """Read one word starting at pos, return the word and next position."""
    parts = []
    while pos < len(line) and not line[pos].isspace():
        match = SEGMENT_PATTERN.match(line, pos)
        if match is None:
            raise ShellError("syntax error: unterminated quote")
        parts.append(convert_segment(match, env))
        pos = match.end()
    return "".join(parts), pos


def split_line(line, env=None):
    """Split a command line into words, expanding environment variables."""
    words = []
    pos = 0
    while pos < len(line):
        if line[pos].isspace():
            pos += 1
            continue
        word, pos = read_word(line, pos, env)
        words.append(word)
    return words


def parse_line(line, env=None):
    """Parse a line into (command, args); return None for empty input."""
    words = split_line(line, env)
    if not words:
        return None
    return words[0], words[1:]
