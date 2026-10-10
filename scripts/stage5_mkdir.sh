#!/usr/bin/env sh
# Stage 5: mkdir and vfs-load, started from the default VFS.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" && ./run.sh --vfs vfs/deep.b64 \
    --script startup/stage5_commands.txt
