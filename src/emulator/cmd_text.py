"""Text commands: tac, tail."""

import re

from emulator.cmd_utils import read_text_file
from emulator.errors import ShellError

DEFAULT_TAIL_LINES = 10
LEGACY_COUNT = re.compile(r"-(\d+)$")


def cmd_tac(shell, args):
    """Print files with lines in reverse order: tac file..."""
    if not args:
        raise ShellError("tac: missing file operand")
    lines = []
    for path in args:
        lines.extend(reversed(read_text_file(shell, "tac", path)))
    return "\n".join(lines)


def parse_count(text):
    """Convert the value of -n to an integer."""
    if not text.isdigit():
        raise ShellError(f"tail: invalid number of lines: '{text}'")
    return int(text)


def take_count(args, index):
    """Return (count, next index) for the option at args[index]."""
    arg = args[index]
    if arg == "-n":
        if index + 1 >= len(args):
            raise ShellError("tail: option requires an argument -- 'n'")
        return parse_count(args[index + 1]), index + 2
    return parse_count(arg[2:]), index + 1


def parse_tail(args):
    """Return (number of lines, files) from tail arguments."""
    count = DEFAULT_TAIL_LINES
    files = []
    index = 0
    while index < len(args):
        arg = args[index]
        legacy = LEGACY_COUNT.match(arg)
        if arg == "--":
            files.extend(args[index + 1:])
            break
        if arg.startswith("-n"):
            count, index = take_count(args, index)
        elif legacy:
            count, index = int(legacy.group(1)), index + 1
        elif arg.startswith("-") and arg != "-":
            raise ShellError(f"tail: invalid option -- '{arg[1]}'")
        else:
            files.append(arg)
            index += 1
    return count, files


def last_lines(lines, count):
    """Return the last count lines."""
    return lines[len(lines) - count:] if count else []


def cmd_tail(shell, args):
    """Print the last lines of files: tail [-n N] file..."""
    count, files = parse_tail(args)
    if not files:
        raise ShellError("tail: missing file operand")
    blocks = []
    for path in files:
        lines = last_lines(read_text_file(shell, "tail", path), count)
        if len(files) > 1:
            lines.insert(0, f"==> {path} <==")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) if len(files) > 1 else blocks[0]
