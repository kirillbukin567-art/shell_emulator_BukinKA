#!/usr/bin/env sh
# Stage 4: all commands of the stage on the VFS with many levels.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --vfs "$ROOT/vfs/deep.b64" \
    --script "$ROOT/startup/stage4_commands.txt"
