"""Entry point: python -m emulator."""

import sys

from emulator.repl import run_repl
from emulator.shell import Shell


def main():
    """Start the interactive shell."""
    run_repl(Shell())
    return 0


if __name__ == "__main__":
    sys.exit(main())
