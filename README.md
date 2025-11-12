# Better Chromium
Better Chromium is a project that applies patches to the Chromium source code to restore functionality and make your browsing experience more private.

**Based on Chromium version: 144.0.7521.1**

## Features

### Privacy & Security
- [x] **Local new tab page** - Uses local new tab page (GrapheneOS)
- [x] **Non-secure origins marked as dangerous** - HTTP sites are marked as DANGEROUS (GrapheneOS)
- [x] **DNS over HTTPS (DoH) improvements** - Secure mode by default, enforced even with inconsistent system DNS (Cromite)
- [x] **Minimal DoH headers** - Reduces HTTP headers in DoH requests to bare minimum (Cromite)
- [x] **Disabled Google API warnings** - Removes annoying warnings about missing Google API keys (Ungoogled Chromium)

### Functionality
- [x] **Manifest Version 2 support** - Restore support for MV2 extensions
- [x] **DuckDuckGo as default search engine** - Privacy-focused search by default
- [x] **Additional search engines** - Enhanced search engine options
- [x] **Close window with last tab** - Flag to control window behavior when closing last tab (Ungoogled Chromium)
