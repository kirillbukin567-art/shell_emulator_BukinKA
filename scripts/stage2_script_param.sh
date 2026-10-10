#!/usr/bin/env sh
# Stage 2: check the --script parameter.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --script "$ROOT/startup/stage1_repl.txt"
