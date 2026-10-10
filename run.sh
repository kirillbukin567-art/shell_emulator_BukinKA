#!/usr/bin/env sh
# Run the emulator: ./run.sh [--vfs PATH] [--script PATH]
ROOT="$(cd "$(dirname "$0")" && pwd)"
PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}" \
    exec python3 -m emulator "$@"
