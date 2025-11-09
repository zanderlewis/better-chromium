#!/usr/bin/env bash
set -euo pipefail

# Master build orchestrator
# Automatically detects what needs to be done

CHROMIUM_DIR="./chromium-src"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "================================================"
echo "Better Chromium - Build Orchestrator"
echo "================================================"
echo ""

# Check if initial setup is needed
if [ ! -d "$CHROMIUM_DIR/src" ]; then
    echo "🔍 Chromium source not found"
    echo "Running full build setup (this will take a while)..."
    echo ""
    exec ./arch-build.sh
fi

# Check if binary exists
if [ ! -f "$CHROMIUM_DIR/src/out/Default/chrome" ]; then
    echo "🔍 Binary not found"
    echo "Running full build..."
    echo ""
    exec ./arch-build.sh
fi

# Check if patches have changed
echo "🔍 Checking for new patches..."
BINARY_MTIME=$(stat -c %Y "$CHROMIUM_DIR/src/out/Default/chrome")
PATCHES_MTIME=0

for patch in ./patches/*.patch; do
    if [ -f "$patch" ]; then
        PATCH_MTIME=$(stat -c %Y "$patch")
        if [ $PATCH_MTIME -gt $PATCHES_MTIME ]; then
            PATCHES_MTIME=$PATCH_MTIME
        fi
    fi
done

if [ $PATCHES_MTIME -gt $BINARY_MTIME ]; then
    echo "✓ New patches detected"
    echo "Running quick rebuild..."
    echo ""
    exec ./quick-rebuild.sh
else
    echo "✓ No changes detected"
    echo ""
    echo "Binary is up to date: $CHROMIUM_DIR/src/out/Default/chrome"
    echo ""
    echo "Options:"
    echo "  ./quick-rebuild.sh    - Rebuild with current patches"
    echo "  ./add-patch.sh <file> - Add a new patch"
    echo "  ./release.sh          - Create release package"
fi
