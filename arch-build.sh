#!/usr/bin/env bash
set -euo pipefail

# Following official Chromium build instructions:
# https://chromium.googlesource.com/chromium/src/+/HEAD/docs/linux/build_instructions.md

PATCHES_DIR="./patches/"
CHROMIUM_DIR="./chromium-src"
DEPOT_TOOLS_DIR="./depot_tools"
OUT_DIR="out/Default"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Disable depot_tools auto-update to avoid rate limiting
export DEPOT_TOOLS_UPDATE=0

# Install build dependencies (Arch Linux)
echo "Installing build dependencies..."
sudo pacman -Syu --needed --noconfirm python perl gcc gcc-libs bison flex gperf pkgconfig \
    nss alsa-lib glib2 gtk3 nspr freetype2 cairo dbus xorg-server-xvfb \
    xorg-xdpyinfo ninja git

# Get depot_tools in project directory
if [ ! -d "$DEPOT_TOOLS_DIR" ]; then
    echo "Cloning depot_tools..."
    cd "$SCRIPT_DIR"
    timeout 300 git clone --depth=1 https://chromium.googlesource.com/chromium/tools/depot_tools.git "$DEPOT_TOOLS_DIR" || {
        echo "Failed to clone depot_tools"
        exit 1
    }
    echo "✓ depot_tools cloned successfully"
else
    echo "✓ depot_tools already exists"
fi

export PATH="$DEPOT_TOOLS_DIR:$PATH"

# Create and enter chromium directory
mkdir -p "$CHROMIUM_DIR"
cd "$CHROMIUM_DIR"

# Fetch chromium source code
if [ ! -d src ]; then
    echo "Fetching Chromium source (this may take a while)..."
    fetch --nohooks --no-history chromium
fi

cd src

# Install additional build dependencies
echo "Installing additional Chromium build dependencies..."
if grep -qi "arch" /etc/os-release; then
    echo "Detected Arch Linux - installing Arch-specific dependencies..."
    # Arch Linux specific dependencies for Chromium
    sudo pacman -Syu --needed --noconfirm \
        python perl gcc gcc-libs bison flex gperf pkgconfig \
        nss alsa-lib glib2 gtk3 nspr freetype2 cairo dbus \
        xorg-server-xvfb xorg-xdpyinfo ninja git libxss \
        libxtst libgnome-keyring cups libpulse ttf-liberation \
        xdg-utils mesa libva libvdpau libxslt libexif libxrandr \
        libxt libxcb libxkbcommon libxkbfile libxinerama libxi libxext \
        libxfixes libxdamage at-spi2-core imagemagick
else
    # For supported distros (Ubuntu, Debian), use the official script
    ./build/install-build-deps.sh
fi

# Apply patches if they exist
if [ -d "$SCRIPT_DIR/$PATCHES_DIR" ]; then
    for patch in "$SCRIPT_DIR/$PATCHES_DIR"/*.patch; do
        if [ -f "$patch" ]; then
            echo "Applying patch $(basename "$patch")..."
            if ! git apply "$patch"; then
                echo "⚠ Warning: Failed to apply patch $(basename "$patch"). Skipping..."
            fi
        fi
    done
    # Commit all patches if any were applied
    if ! git diff --cached --quiet 2>/dev/null; then
        git add -A
        git commit -m "Applied custom patches"
    fi
fi

# Run hooks
echo "Running gclient hooks..."
gclient runhooks

# Configure build
echo "Configuring build..."
# Use mold linker for faster linking and enable high parallelism with 96GB RAM
gn gen "$OUT_DIR" --args='is_debug=false enable_nacl=false is_component_build=false symbol_level=0 use_mold=true'

# Build Chromium with maximum parallelism
echo "Building Chromium..."
# Calculate optimal job count: ~2 jobs per core + extra headroom for 96GB RAM
NUM_JOBS=$(($(nproc) * 2 + 4))
echo "Building with $NUM_JOBS parallel jobs..."
ninja -C "$OUT_DIR" -j "$NUM_JOBS" chrome

# Show completion message
BINARY_PATH="$PWD/$OUT_DIR/chrome"
echo ""
echo "================================================"
echo "Chromium build complete!"
echo "Binary location: $BINARY_PATH"
echo "Run with: $BINARY_PATH"
echo "================================================"
