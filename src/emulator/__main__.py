"""Entry point: python -m emulator."""

import sys

from emulator.config import format_debug, parse_config
from emulator.errors import ShellError
from emulator.repl import run_repl
from emulator.script import run_script
from emulator.shell import Shell


def main(argv=None):
    """Start the emulator: print parameters, run script, then dialog."""
    config = parse_config(argv)
    print("\n".join(format_debug(config)))
    try:
        shell = Shell(vfs_path=config.vfs_path)
        if config.script_path:
            run_script(shell, config.script_path)
    except ShellError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    run_repl(shell)
    return 0


if __name__ == "__main__":
    sys.exit(main())
