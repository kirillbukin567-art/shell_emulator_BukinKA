"""Command line parameters of the emulator."""

import argparse
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Parameters given by the user at start."""

    vfs_path: Optional[str] = None
    script_path: Optional[str] = None


def build_arg_parser():
    """Create the parser of command line arguments."""
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="Emulator of a UNIX-like shell with an in-memory VFS.",
    )
    parser.add_argument(
        "--vfs", metavar="PATH", dest="vfs_path",
        help="path to the physical location of the VFS",
    )
    parser.add_argument(
        "--script", metavar="PATH", dest="script_path",
        help="path to the startup script with emulator commands",
    )
    return parser


def parse_config(argv=None):
    """Read the parameters from argv (default: sys.argv)."""
    namespace = build_arg_parser().parse_args(argv)
    return Config(namespace.vfs_path, namespace.script_path)


def format_debug(config):
    """Return debug lines that show all given parameters."""
    return [
        "[debug] parameters:",
        f"[debug]   vfs    = {config.vfs_path}",
        f"[debug]   script = {config.script_path}",
    ]
