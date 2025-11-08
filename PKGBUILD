# Maintainer: Zander Lewis <zander@zanderlewis.dev>
pkgname=better-chromium
pkgver=LATEST_VERSION
pkgrel=1
pkgdesc="Chromium with patches for MV2 support and more."
arch=('x86_64')
url="https://github.com/zanderlewis/better-chromium"
license=('BSD')
depends=('glib2' 'gtk3' 'libxss' 'alsa-lib' 'cups' 'libpulse' 'libva')
optdepends=('ttf-liberation: for font rendering')
source=("${pkgname}-${pkgver}-linux-x86_64.tar.gz::https://github.com/zanderlewis/better-chromium/releases/download/v${pkgver}/better-chromium-${pkgver}-linux-x86_64.tar.gz")
sha256sums=('SKIP')  # Update this with actual sha256sum

package() {
    install -d "$pkgdir/opt/better-chromium"
    cp -r "$srcdir/better-chromium"/* "$pkgdir/opt/better-chromium/"
    
    # Create symlink in /usr/bin
    install -d "$pkgdir/usr/bin"
    ln -s /opt/better-chromium/better-chromium "$pkgdir/usr/bin/better-chromium"
    
    # Install chrome_sandbox with proper permissions
    chmod 4555 "$pkgdir/opt/better-chromium/chrome_sandbox" 2>/dev/null || true
}
