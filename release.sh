#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="$SCRIPT_DIR/chromium-src/src/out/Default"
RELEASE_DIR="$SCRIPT_DIR/release-build"
VERSION=$(git describe --tags --always 2>/dev/null || echo "dev")

echo "Creating GitHub release package..."

# Remove old release tarballs to avoid confusion
echo "Cleaning up old releases..."
rm -f "$SCRIPT_DIR"/better-chromium-*.tar.gz

# Clean and create release directory
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR/better-chromium"

echo "Copying binaries and resources..."

# Copy the main binary and wrapper
cp "$OUT_DIR/chrome" "$RELEASE_DIR/better-chromium/"
cp "$OUT_DIR/chrome-wrapper" "$RELEASE_DIR/better-chromium/" 2>/dev/null || true
cp "$OUT_DIR/chrome_sandbox" "$RELEASE_DIR/better-chromium/" 2>/dev/null || true
cp "$OUT_DIR/chrome_crashpad_handler" "$RELEASE_DIR/better-chromium/" 2>/dev/null || true

# Copy all .pak files (UI resources)
cp "$OUT_DIR"/chrome*.pak "$RELEASE_DIR/better-chromium/" 2>/dev/null || true
cp "$OUT_DIR"/resources*.pak "$RELEASE_DIR/better-chromium/" 2>/dev/null || true

# Copy resources and locales directories
cp -r "$OUT_DIR/resources" "$RELEASE_DIR/better-chromium/" 2>/dev/null || true
cp -r "$OUT_DIR/locales" "$RELEASE_DIR/better-chromium/" 2>/dev/null || true

# Copy data files
cp "$OUT_DIR"/icudtl.dat "$RELEASE_DIR/better-chromium/" 2>/dev/null || true
cp "$OUT_DIR"/snapshot_blob.bin "$RELEASE_DIR/better-chromium/" 2>/dev/null || true
cp "$OUT_DIR"/v8_context_snapshot.bin "$RELEASE_DIR/better-chromium/" 2>/dev/null || true

# Copy shared libraries (.so files)
echo "Copying shared libraries..."
cp "$OUT_DIR"/*.so "$RELEASE_DIR/better-chromium/" 2>/dev/null || true
cp "$OUT_DIR"/*.so.* "$RELEASE_DIR/better-chromium/" 2>/dev/null || true

# Create a launcher script
cat > "$RELEASE_DIR/better-chromium/better-chromium" << 'EOF'
#!/usr/bin/env bash
# Better Chromium launcher - standalone package
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set library path to use bundled libraries
export LD_LIBRARY_PATH="$SCRIPT_DIR:$LD_LIBRARY_PATH"

# Run chrome with necessary flags for standalone mode
exec "$SCRIPT_DIR/chrome" \
    --no-sandbox \
    "$@"
EOF
chmod +x "$RELEASE_DIR/better-chromium/better-chromium"

# Create README for release
cat > "$RELEASE_DIR/better-chromium/README.md" << 'EOF'
# Release 11.08.25.12PM.2
This release changes the default search engine to DuckDuckGo. Using Chromium built on 11/08/25 at 12PM
EOF

echo "Setting permissions..."
# Make executables
chmod +x "$RELEASE_DIR/better-chromium/chrome" 2>/dev/null || true
chmod +x "$RELEASE_DIR/better-chromium/chrome_sandbox" 2>/dev/null || true
chmod +x "$RELEASE_DIR/better-chromium/chrome_crashpad_handler" 2>/dev/null || true
chmod +x "$RELEASE_DIR/better-chromium/chrome-wrapper" 2>/dev/null || true
# Make all .so files readable
chmod 644 "$RELEASE_DIR/better-chromium"/*.so* 2>/dev/null || true

# Create tarball
ARCHIVE_NAME="better-chromium-${VERSION}-linux-x86_64.tar.gz"
cd "$RELEASE_DIR"
tar czf "$ARCHIVE_NAME" better-chromium/
mv "$ARCHIVE_NAME" "$SCRIPT_DIR/"

echo "✓ Release package created: $SCRIPT_DIR/$ARCHIVE_NAME"
echo ""
echo "Next steps:"
echo "1. Create a GitHub release:"
echo "   gh release create v${VERSION} $SCRIPT_DIR/$ARCHIVE_NAME"
echo ""
echo "2. Users can extract and run with:"
echo "   tar xzf $ARCHIVE_NAME"
echo "   ./better-chromium/better-chromium"
