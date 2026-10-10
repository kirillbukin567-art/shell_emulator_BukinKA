#!/usr/bin/env sh
# Stage 3: VFS with several files.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --vfs "$ROOT/vfs/files.b64" \
    --script "$ROOT/startup/stage3_vfs.txt"
