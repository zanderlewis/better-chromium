#!/usr/bin/env bash
set -uo pipefail

# Quick rebuild script - only rebuilds after applying new patches
# Use this when you've added new patches or made changes to source
# Much faster than full build since Chromium sources are already present

PATCHES_DIR="./patches/"
CHROMIUM_DIR="./chromium-src"
DEPOT_TOOLS_DIR="./depot_tools"
OUT_DIR="out/Default"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Disable depot_tools auto-update
export DEPOT_TOOLS_UPDATE=0
export PATH="$DEPOT_TOOLS_DIR:$PATH"

echo "================================================"
echo "Better Chromium - Quick Rebuild"
echo "================================================"

# Check if source exists
if [ ! -d "$CHROMIUM_DIR/src" ]; then
    echo "❌ Chromium source not found. Run ./arch-build.sh first to do initial setup."
    exit 1
fi

cd "$CHROMIUM_DIR/src"

# Reset any previous patches to clean state
echo "Resetting to clean state..."
git reset --hard HEAD
git clean -fd

# Apply patches
if [ -d "$SCRIPT_DIR/$PATCHES_DIR" ]; then
    echo "Applying patches..."
    PATCH_COUNT=0
    for patch in "$SCRIPT_DIR/$PATCHES_DIR"/*.patch; do
        if [ -f "$patch" ]; then
            echo "  Applying $(basename "$patch")..."
            if ! git apply "$patch"; then
                echo "⚠ Warning: Failed to apply patch $(basename "$patch"). Skipping..."
            else
                PATCH_COUNT=$((PATCH_COUNT + 1))
            fi
        fi
    done
    echo "✓ Applied $PATCH_COUNT patches"
    
    # Commit patches if any were applied
    if ! git diff --cached --quiet 2>/dev/null; then
        git add -A
        git commit -m "Applied custom patches" || true
    fi
fi

# Run hooks (if needed for new dependencies)
echo "Running gclient hooks..."
gclient runhooks || echo "⚠ Warning: gclient hooks had issues, continuing anyway..."

# Rebuild
echo "Rebuilding Chromium with changes..."
NUM_JOBS=$(($(nproc) * 2 + 4))
echo "Building with $NUM_JOBS parallel jobs..."
ninja -C "$OUT_DIR" -j "$NUM_JOBS" chrome

BINARY_PATH="$PWD/$OUT_DIR/chrome"
echo ""
echo "================================================"
echo "✓ Rebuild complete!"
echo "Binary location: $BINARY_PATH"
echo "================================================"
echo ""
echo "Next: Run './release.sh' to create release package"
