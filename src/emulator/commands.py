"""Shell commands. Every command takes the shell and a list of arguments."""

from emulator.errors import ShellError


def format_stub(name, args):
    """Build the output of a stub command: its name and arguments."""
    return " ".join([name] + args)


def cmd_ls(shell, args):
    """Stub of the ls command."""
    return format_stub("ls", args)


def cmd_cd(shell, args):
    """Stub of the cd command."""
    return format_stub("cd", args)


def cmd_exit(shell, args):
    """Stop the shell."""
    shell.running = False
    return ""


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}


def run_command(shell, name, args):
    """Run a command by name and return its output."""
    handler = COMMANDS.get(name)
    if handler is None:
        raise ShellError(f"{name}: command not found")
    return handler(shell, args)
