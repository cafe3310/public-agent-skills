#!/bin/bash
set -euo pipefail

OUTPUT_PATH="$1"

if [ -z "$OUTPUT_PATH" ]; then
  echo "Error: Output file path not specified." >&2
  echo "Usage: $0 /path/to/your/image.png" >&2
  exit 1
fi

OUTPUT_DIR=$(dirname "$OUTPUT_PATH")
if [ ! -d "$OUTPUT_DIR" ]; then
  echo "Error: Output directory '$OUTPUT_DIR' does not exist." >&2
  exit 1
fi

# Use osascript to write the PNG data from the clipboard directly to the target file.
# This command returns a non-zero exit code if the clipboard doesn't contain PNG data.
if ! osascript -e "on run {p}" -e "write (the clipboard as «class PNGf») to (open for access POSIX file p with write permission)" -e "end" -- "$OUTPUT_PATH"; then
  echo "Error: Could not get image from clipboard. Clipboard may not contain an image." >&2
  # Clean up empty file that might have been created
  rm -f "$OUTPUT_PATH"
  exit 1
fi

echo "Image successfully pasted to $OUTPUT_PATH"
