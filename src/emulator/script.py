"""Startup script: commands executed one after another."""

from emulator.errors import ShellError
from emulator.repl import run_line


def read_script(path):
    """Return the lines of a script file."""
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read().splitlines()
    except (OSError, UnicodeDecodeError) as error:
        raise ShellError(f"cannot read script '{path}': {error}") from error


def is_skipped(line):
    """Blank lines and lines that start with # are not executed."""
    stripped = line.strip()
    return not stripped or stripped.startswith("#")


def run_script(shell, path, output=print):
    """Run a script, show input and output as in a real dialog.

    Lines that fail are reported and skipped. Return the number of
    failed lines.
    """
    failed = 0
    for line in read_script(path):
        if is_skipped(line):
            continue
        output(f"{shell.prompt()}{line}")
        if not run_line(shell, line, output):
            failed += 1
        if not shell.running:
            break
    return failed
