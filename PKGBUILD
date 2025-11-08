# Maintainer: Zander Lewis <zander@zanderlewis.dev>
pkgname=better-chromium
pkgver=11.08.25.12PM
pkgrel=1
pkgdesc="Chromium with patches for MV2 support and more."
arch=('x86_64')
url="https://github.com/zanderlewis/better-chromium"
license=('BSD')
depends=('glib2' 'gtk3' 'libxss' 'alsa-lib' 'cups' 'libpulse' 'libva')
optdepends=('ttf-liberation: for font rendering')
source=("${pkgname}-${pkgver}-linux-x86_64.tar.gz::https://github.com/zanderlewis/better-chromium/releases/download/v${pkgver}/better-chromium-${pkgver}-linux-x86_64.tar.gz")
sha256sums=('0980ba8591fdc41c87b6db8c7fcf46ef3a24f8140eab809a5e1ea474b0abdba5')

package() {
    install -d "$pkgdir/opt/better-chromium"
    cp -r "$srcdir/better-chromium"/* "$pkgdir/opt/better-chromium/"
    
    # Create symlink in /usr/bin
    install -d "$pkgdir/usr/bin"
    ln -s /opt/better-chromium/better-chromium "$pkgdir/usr/bin/better-chromium"
    
    # Install chrome_sandbox with proper permissions
    chmod 4555 "$pkgdir/opt/better-chromium/chrome_sandbox" 2>/dev/null || true
}
