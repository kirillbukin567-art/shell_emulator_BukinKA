#!/usr/bin/env sh
# Stage 3: minimal VFS (a single file).
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --vfs "$ROOT/vfs/minimal.b64" \
    --script "$ROOT/startup/stage3_vfs.txt"
