#!/usr/bin/env sh
# Stage 2: check both parameters together, with erroneous lines.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --vfs "$ROOT/vfs/files.b64" \
    --script "$ROOT/startup/stage2_errors.txt"
