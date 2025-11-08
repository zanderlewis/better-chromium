#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="$SCRIPT_DIR/chromium-src/src/out/Default"
RELEASE_DIR="$SCRIPT_DIR/release-build"
VERSION=$(git describe --tags --always 2>/dev/null || echo "dev")

echo "Creating GitHub release package..."

# Clean and create release directory
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR/better-chromium"

# Copy the binary and essential files
cp "$OUT_DIR/chrome" "$RELEASE_DIR/better-chromium/"
cp "$OUT_DIR/chrome_sandbox" "$RELEASE_DIR/better-chromium/" 2>/dev/null || true

# Copy resources and libraries
cp -r "$OUT_DIR/resources" "$RELEASE_DIR/better-chromium/" 2>/dev/null || true
cp -r "$OUT_DIR/locales" "$RELEASE_DIR/better-chromium/" 2>/dev/null || true

# Copy ICU data
cp "$OUT_DIR/icudtl.dat" "$RELEASE_DIR/better-chromium/" 2>/dev/null || true

# Create a launcher script
cat > "$RELEASE_DIR/better-chromium/better-chromium" << 'EOF'
#!/usr/bin/env bash
# Better Chromium launcher
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export LD_LIBRARY_PATH="$SCRIPT_DIR:$LD_LIBRARY_PATH"
exec "$SCRIPT_DIR/chrome" "$@"
EOF
chmod +x "$RELEASE_DIR/better-chromium/better-chromium"

# Create README for release
cat > "$RELEASE_DIR/better-chromium/README.md" << 'EOF'
# Release 11.08.25.12PM
This is the initial release of Better Chromium and features Manifest v2 support. Built on 11/08/25 at 12PM
```
EOF

# Make the chrome executable
chmod +x "$RELEASE_DIR/better-chromium/chrome"

# Create tarball
ARCHIVE_NAME="better-chromium-${VERSION}-linux-x86_64.tar.gz"
cd "$RELEASE_DIR"
tar czf "$ARCHIVE_NAME" better-chromium/
mv "$ARCHIVE_NAME" "$SCRIPT_DIR/"

echo "✓ Release package created: $SCRIPT_DIR/$ARCHIVE_NAME"
echo ""
echo "Next steps:"
echo "1. Create a GitHub release"
echo "2. Upload $ARCHIVE_NAME as an asset"
echo ""
echo "Users can extract with:"
echo "  tar xzf $ARCHIVE_NAME"
echo "  ./better-chromium/better-chromium"
