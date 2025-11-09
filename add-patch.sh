#!/usr/bin/env bash
set -euo pipefail

# Add new patch to Better Chromium
# Usage: ./add-patch.sh <patch-file> [patch-name]

PATCHES_DIR="./patches/"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -lt 1 ]; then
    echo "Usage: $0 <patch-file> [optional-name]"
    echo ""
    echo "Example:"
    echo "  $0 /path/to/my.patch"
    echo "  $0 /path/to/my.patch my-feature"
    exit 1
fi

PATCH_FILE="$1"
PATCH_NAME="${2:-$(basename "$PATCH_FILE")}"

if [ ! -f "$PATCH_FILE" ]; then
    echo "❌ Patch file not found: $PATCH_FILE"
    exit 1
fi

mkdir -p "$SCRIPT_DIR/$PATCHES_DIR"
DEST_PATH="$SCRIPT_DIR/$PATCHES_DIR/$PATCH_NAME"

# Make sure it ends with .patch
if [[ "$DEST_PATH" != *.patch ]]; then
    DEST_PATH="${DEST_PATH}.patch"
fi

cp "$PATCH_FILE" "$DEST_PATH"
echo "✓ Patch added: $DEST_PATH"
echo ""
echo "Now run: ./quick-rebuild.sh"
