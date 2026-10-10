"""Create VFS objects: default one and loaded from ZIP or base64 text."""

import base64
import binascii
import io
import posixpath
import zipfile

from emulator.errors import ShellError
from emulator.vfs import Vfs, normalize

DEFAULT_FILES = {
    "/readme.txt": "Default VFS.\nUse vfs-load to open another one.\n",
    "/docs/notes.txt": "first\nsecond\nthird\n",
}


def default_vfs():
    """Build the VFS that is used when nothing is loaded."""
    vfs = Vfs()
    for path, text in DEFAULT_FILES.items():
        vfs.add_file(path, text.encode("utf-8"))
    return vfs


def unwrap_container(raw):
    """Return ZIP bytes from raw ZIP data or from its base64 text."""
    if zipfile.is_zipfile(io.BytesIO(raw)):
        return raw
    try:
        decoded = base64.b64decode(b"".join(raw.split()), validate=True)
    except (binascii.Error, ValueError) as error:
        raise ShellError("not a ZIP archive or base64 text") from error
    if not zipfile.is_zipfile(io.BytesIO(decoded)):
        raise ShellError("base64 data is not a ZIP archive")
    return decoded


def fill_from_zip(vfs, archive):
    """Copy entries of an open ZIP file into the VFS (memory only)."""
    for info in archive.infolist():
        path = normalize(info.filename)
        if path == "/":
            continue
        if info.is_dir():
            vfs.add_dir(path)
        else:
            vfs.add_file(path, archive.read(info))


def vfs_from_bytes(raw, name):
    """Create a VFS from ZIP bytes or base64 text of a ZIP archive."""
    data = unwrap_container(raw)
    vfs = Vfs(name)
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            fill_from_zip(vfs, archive)
    except (zipfile.BadZipFile, NotADirectoryError, KeyError) as error:
        raise ShellError(f"broken VFS archive: {error}") from error
    return vfs


def load_vfs(path):
    """Read a VFS from a file on disk; its name is the file name."""
    try:
        with open(path, "rb") as handle:
            raw = handle.read()
    except OSError as error:
        raise ShellError(f"cannot read VFS '{path}': {error.strerror}") \
            from error
    name = posixpath.splitext(posixpath.basename(path))[0]
    return vfs_from_bytes(raw, name or "vfs")
