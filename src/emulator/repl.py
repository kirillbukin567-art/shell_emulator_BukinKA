"""Interactive read-eval-print loop."""

from emulator.errors import ShellError


def run_line(shell, line, output=print):
    """Execute a line; print the result or the error message."""
    try:
        result = shell.execute(line)
    except ShellError as error:
        output(f"error: {error}")
        return False
    if result:
        output(result)
    return True


def run_repl(shell, input_fn=input, output=print):
    """Read commands until exit or end of input."""
    while shell.running:
        try:
            line = input_fn(shell.prompt())
        except EOFError:
            output("")
            break
        except KeyboardInterrupt:
            output("")
            continue
        run_line(shell, line, output)
