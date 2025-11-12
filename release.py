#!/usr/bin/env python3
"""
Create GitHub release package for Better Chromium
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import glob

# Configuration
SCRIPT_DIR = Path(__file__).parent.resolve()
OUT_DIR = SCRIPT_DIR / "chromium-src" / "src" / "out" / "Default"
RELEASE_DIR = SCRIPT_DIR / "release-build"


def run_command(cmd, cwd=None, check=True, capture_output=False):
    """Execute a command and handle errors."""
    if isinstance(cmd, list):
        cmd_str = " ".join(cmd)
    else:
        cmd_str = cmd
        
    print(f"Running: {cmd_str}")
    
    result = subprocess.run(
        cmd,
        cwd=cwd,
        check=check,
        capture_output=capture_output,
        text=True
    )
    
    return result


def get_version():
    """Get version from git or use 'dev'."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return "dev"


def clean_old_releases():
    """Remove old release tarballs."""
    print("Cleaning up old releases...")
    for tarball in SCRIPT_DIR.glob("better-chromium-*.tar.gz"):
        tarball.unlink()
        print(f"  Removed: {tarball.name}")


def copy_files(src, dest, pattern="*"):
    """Copy files matching pattern from src to dest."""
    files = glob.glob(str(src / pattern))
    copied = 0
    for file in files:
        try:
            if os.path.isfile(file):
                shutil.copy2(file, dest)
                copied += 1
        except Exception as e:
            print(f"  Warning: Could not copy {file}: {e}")
    return copied


def copy_directory(src, dest):
    """Copy directory if it exists."""
    if src.exists():
        try:
            shutil.copytree(src, dest)
            return True
        except Exception as e:
            print(f"  Warning: Could not copy {src}: {e}")
    return False


def main():
    """Create release package."""
    print("Creating GitHub release package...")
    print()
    
    # Check if binary exists
    chrome_binary = OUT_DIR / "chrome"
    if not chrome_binary.exists():
        print(f"❌ Chrome binary not found at: {chrome_binary}")
        print("Run ./arch_build.py or ./quick_rebuild.py first")
        sys.exit(1)
    
    version = get_version()
    clean_old_releases()
    
    # Clean and create release directory
    if RELEASE_DIR.exists():
        shutil.rmtree(RELEASE_DIR)
    
    release_app_dir = RELEASE_DIR / "better-chromium"
    release_app_dir.mkdir(parents=True)
    
    print("Copying binaries and resources...")
    
    # Copy main binaries
    for binary in ["chrome", "chrome-wrapper", "chrome_sandbox", "chrome_crashpad_handler"]:
        src = OUT_DIR / binary
        if src.exists():
            shutil.copy2(src, release_app_dir)
            print(f"  ✓ {binary}")
    
    # Copy .pak files
    print("Copying resource files...")
    pak_count = copy_files(OUT_DIR, release_app_dir, "*.pak")
    print(f"  ✓ Copied {pak_count} .pak files")
    
    # Copy directories
    for dir_name in ["resources", "locales"]:
        src_dir = OUT_DIR / dir_name
        dest_dir = release_app_dir / dir_name
        if copy_directory(src_dir, dest_dir):
            print(f"  ✓ {dir_name}/")
    
    # Copy data files
    print("Copying data files...")
    for data_file in ["icudtl.dat", "snapshot_blob.bin", "v8_context_snapshot.bin"]:
        src = OUT_DIR / data_file
        if src.exists():
            shutil.copy2(src, release_app_dir)
            print(f"  ✓ {data_file}")
    
    # Copy shared libraries
    print("Copying shared libraries...")
    so_count = copy_files(OUT_DIR, release_app_dir, "*.so")
    so_count += copy_files(OUT_DIR, release_app_dir, "*.so.*")
    print(f"  ✓ Copied {so_count} library files")
    
    # Create launcher script
    launcher_path = release_app_dir / "better-chromium"
    with open(launcher_path, 'w') as f:
        f.write('''#!/usr/bin/env bash
# Better Chromium launcher - standalone package
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set library path to use bundled libraries
export LD_LIBRARY_PATH="$SCRIPT_DIR:$LD_LIBRARY_PATH"

# Run chrome with necessary flags for standalone mode
exec "$SCRIPT_DIR/chrome" \\
    --no-sandbox \\
    "$@"
''')
    launcher_path.chmod(0o755)
    print("  ✓ Created launcher script")
    
    # Set permissions
    print("Setting permissions...")
    for binary in ["chrome", "chrome_sandbox", "chrome_crashpad_handler", "chrome-wrapper"]:
        binary_path = release_app_dir / binary
        if binary_path.exists():
            binary_path.chmod(0o755)
    
    for so_file in release_app_dir.glob("*.so*"):
        so_file.chmod(0o644)
    
    # Create tarball
    archive_name = f"better-chromium-{version}-linux-x86_64.tar.gz"
    print(f"\nCreating tarball: {archive_name}")
    
    result = run_command(
        ["tar", "czf", archive_name, "better-chromium/"],
        cwd=RELEASE_DIR,
        check=True
    )
    
    # Move tarball to script directory
    shutil.move(RELEASE_DIR / archive_name, SCRIPT_DIR / archive_name)
    
    print()
    print("=" * 60)
    print(f"✓ Release package created: {SCRIPT_DIR / archive_name}")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Create a GitHub release:")
    print(f"   gh release create v{version} {SCRIPT_DIR / archive_name}")
    print()
    print("2. Users can extract and run with:")
    print(f"   tar xzf {archive_name}")
    print("   ./better-chromium/better-chromium")


if __name__ == "__main__":
    main()
