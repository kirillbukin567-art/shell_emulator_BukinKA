#!/usr/bin/env sh
# Stage 3: broken and missing VFS files are reported.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --vfs "$ROOT/README.md"
echo "exit code: $?"
"$ROOT/run.sh" --vfs "$ROOT/vfs/missing.b64"
echo "exit code: $?"
