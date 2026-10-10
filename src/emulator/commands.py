"""Shell commands. Every command takes the shell and a list of arguments."""

from emulator.cmd_find import cmd_find
from emulator.cmd_nav import cmd_cd, cmd_ls, cmd_pwd
from emulator.cmd_text import cmd_tac, cmd_tail
from emulator.errors import ShellError


def cmd_exit(shell, args):
    """Stop the shell."""
    shell.running = False
    return ""


def cmd_vfs_init(shell, args):
    """Replace the current VFS by the default one."""
    if args:
        raise ShellError("vfs-init: too many arguments")
    shell.reset_vfs()
    return ""


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "pwd": cmd_pwd,
    "tac": cmd_tac,
    "tail": cmd_tail,
    "find": cmd_find,
    "exit": cmd_exit,
    "vfs-init": cmd_vfs_init,
}


def run_command(shell, name, args):
    """Run a command by name and return its output."""
    handler = COMMANDS.get(name)
    if handler is None:
        raise ShellError(f"{name}: command not found")
    return handler(shell, args)
