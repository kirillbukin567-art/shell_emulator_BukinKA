#!/usr/bin/env sh
# Stage 2: check the --vfs parameter (debug output shows it).
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
printf 'exit\n' | "$ROOT/run.sh" --vfs "$ROOT/vfs/files.b64"
