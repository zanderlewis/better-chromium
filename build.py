#!/usr/bin/env python3
"""
Better Chromium - Master build orchestrator
Automatically detects what needs to be done
"""

import sys
import subprocess
from pathlib import Path
import os

# Configuration
SCRIPT_DIR = Path(__file__).parent.resolve()
CHROMIUM_DIR = SCRIPT_DIR / "chromium-src"
PATCHES_DIR = SCRIPT_DIR / "patches"


def run_script(script_name):
    """Execute a Python script."""
    script_path = SCRIPT_DIR / script_name
    print(f"\nExecuting: {script_name}")
    print("=" * 60)
    result = subprocess.run([sys.executable, str(script_path)])
    sys.exit(result.returncode)


def get_mtime(path):
    """Get modification time of a file."""
    try:
        return path.stat().st_mtime
    except:
        return 0


def main():
    """Main build orchestration."""
    print("=" * 60)
    print("Better Chromium - Build Orchestrator")
    print("=" * 60)
    print()
    
    src_dir = CHROMIUM_DIR / "src"
    binary_path = src_dir / "out" / "Default" / "chrome"
    
    # Check if initial setup is needed
    if not src_dir.exists():
        print("🔍 Chromium source not found")
        print("Running full build setup (this will take a while)...")
        print()
        run_script("arch_build.py")
    
    # Check if binary exists
    if not binary_path.exists():
        print("🔍 Binary not found")
        print("Running full build...")
        print()
        run_script("arch_build.py")
    
    # Check if patches have changed
    print("🔍 Checking for new patches...")
    binary_mtime = get_mtime(binary_path)
    patches_mtime = 0
    
    # Check all patch files
    for patch_file in PATCHES_DIR.glob("*.patch"):
        patch_mtime = get_mtime(patch_file)
        if patch_mtime > patches_mtime:
            patches_mtime = patch_mtime
    
    # Check series file
    series_file = PATCHES_DIR / "series"
    if series_file.exists():
        series_mtime = get_mtime(series_file)
        if series_mtime > patches_mtime:
            patches_mtime = series_mtime
    
    if patches_mtime > binary_mtime:
        print("✓ New patches detected")
        print("Running quick rebuild...")
        print()
        run_script("quick_rebuild.py")
    else:
        print("✓ No changes detected")
        print()
        print(f"Binary is up to date: {binary_path}")
        print()
        print("Options:")
        print("  ./quick_rebuild.py    - Rebuild with current patches")
        print("  ./add_patch.py <file> - Add a new patch")
        print("  ./release.py          - Create release package")
        print()
        print("To run Chromium:")
        print(f"  {binary_path}")


if __name__ == "__main__":
    main()
