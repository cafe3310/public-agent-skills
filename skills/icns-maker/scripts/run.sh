#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="$(which python3 || echo "python3")"

if [ $# -eq 0 ]; then
  echo "Usage: $0 <png-file-or-dir> [output-path-or-dir] [additional-args...]"
  echo "Example: $0 ~/Downloads/icons"
  echo "Example: $0 icon.png app.icns"
  exit 1
fi

INPUT="$1"
OUTPUT="${2:-}"

EXTRA_ARGS=()
if [ -n "$OUTPUT" ]; then
  EXTRA_ARGS+=("-o" "$OUTPUT")
  shift 2 || shift 1
  EXTRA_ARGS+=("$@")
else
  shift 1
  EXTRA_ARGS+=("$@")
fi

exec "$PYTHON_BIN" "$SCRIPT_DIR/make_icns.py" "$INPUT" "${EXTRA_ARGS[@]}"
