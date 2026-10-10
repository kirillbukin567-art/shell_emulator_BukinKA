#!/usr/bin/env sh
# Stage 5: one script that checks every command of every stage.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --vfs "$ROOT/vfs/deep.b64" \
    --script "$ROOT/startup/stage_all.txt"
