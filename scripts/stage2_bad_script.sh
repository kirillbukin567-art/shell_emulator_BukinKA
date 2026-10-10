#!/usr/bin/env sh
# Stage 2: a missing startup script is reported with a non-zero code.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --script "$ROOT/startup/does_not_exist.txt"
echo "exit code: $?"
