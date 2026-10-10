"""Generate demo VFS archives as base64 text files in the vfs/ folder."""

import base64
import io
import sys
import zipfile
from pathlib import Path

FIXED_DATE = (2026, 1, 1, 0, 0, 0)
BINARY_BLOB = bytes(range(256))

MINIMAL = {"hello.txt": b"Hello, VFS!\n"}

FILES = {
    "a.txt": b"alpha\nbeta\ngamma\n",
    "b.txt": b"one\ntwo\n",
    "log.txt": "".join(f"line {n}\n" for n in range(1, 16)).encode(),
    "empty.txt": b"",
    "unicode.txt": "привет\nмир\n".encode("utf-8"),
}

DEEP = {
    "readme.txt": b"Deep VFS with several levels.\n",
    "docs/guide.txt": b"guide 1\nguide 2\nguide 3\n",
    "docs/api/v1/spec.txt": b"GET /a\nPOST /b\n",
    "docs/api/v1/notes.md": b"# Notes\ntext\n",
    "docs/api/v2/spec.txt": b"GET /a\nGET /c\nDELETE /d\n",
    "src/main.py": b"print('hi')\n",
    "src/lib/util/helpers.py": b"def f():\n    return 1\n",
    "bin/data.bin": BINARY_BLOB,
    "empty_dir/": b"",
}

ARCHIVES = {"minimal": MINIMAL, "files": FILES, "deep": DEEP}


def build_zip(entries):
    """Return ZIP bytes for a dict {path: data}; a '/' ending is a dir."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for path, data in entries.items():
            info = zipfile.ZipInfo(path, FIXED_DATE)
            if path.endswith("/"):
                info.external_attr = 0o40755 << 16
            archive.writestr(info, data)
    return buffer.getvalue()


def main():
    """Write base64 text of every demo archive."""
    target = Path(__file__).resolve().parent.parent / "vfs"
    target.mkdir(exist_ok=True)
    for name, entries in ARCHIVES.items():
        text = base64.encodebytes(build_zip(entries)).decode("ascii")
        (target / f"{name}.b64").write_text(text, encoding="ascii")
        print(f"written vfs/{name}.b64")
    return 0


if __name__ == "__main__":
    sys.exit(main())
