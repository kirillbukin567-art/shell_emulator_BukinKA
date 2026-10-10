#!/usr/bin/env sh
# Stage 4: text commands on the VFS with several files.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --vfs "$ROOT/vfs/files.b64" \
    --script "$ROOT/startup/stage4_files.txt"
