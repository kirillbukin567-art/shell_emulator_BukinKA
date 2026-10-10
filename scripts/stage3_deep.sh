#!/usr/bin/env sh
# Stage 3: VFS with 3+ levels of folders and files.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --vfs "$ROOT/vfs/deep.b64" \
    --script "$ROOT/startup/stage3_vfs.txt"
