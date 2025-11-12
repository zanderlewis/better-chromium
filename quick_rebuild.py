#!/usr/bin/env python3
"""
Quick rebuild script - only rebuilds after applying new patches
Use this when you've added new patches or made changes to source
Much faster than full build since Chromium sources are already present
"""

import os
import sys
import subprocess
import multiprocessing
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent.resolve()
PATCHES_DIR = SCRIPT_DIR / "patches"
CHROMIUM_DIR = SCRIPT_DIR / "chromium-src"
DEPOT_TOOLS_DIR = SCRIPT_DIR / "depot_tools"
OUT_DIR = "out/Default"

# Disable depot_tools auto-update
os.environ["DEPOT_TOOLS_UPDATE"] = "0"


def run_command(cmd, cwd=None, check=True):
    """Execute a command and handle errors."""
    if isinstance(cmd, list):
        cmd_str = " ".join(cmd)
    else:
        cmd_str = cmd
        
    print(f"Running: {cmd_str}")
    
    result = subprocess.run(
        cmd,
        cwd=cwd,
        check=False,
        capture_output=False,
        text=True
    )
    
    if check and result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    
    return result


def main():
    """Quick rebuild with patches."""
    print("=" * 48)
    print("Better Chromium - Quick Rebuild")
    print("=" * 48)
    print()
    
    src_dir = CHROMIUM_DIR / "src"
    
    # Check if source exists
    if not src_dir.exists():
        print("❌ Chromium source not found. Run ./arch_build.py first to do initial setup.")
        sys.exit(1)
    
    # Add depot_tools to PATH
    os.environ["PATH"] = f"{DEPOT_TOOLS_DIR}:{os.environ['PATH']}"
    
    os.chdir(src_dir)
    
    # Set up quilt environment
    os.environ["QUILT_PATCHES"] = str(PATCHES_DIR)
    
    # Pop all patches (reset to clean state)
    print("Resetting to clean state...")
    result = run_command(["quilt", "pop", "-a"], check=False)
    if result.returncode not in (0, 2):
        print("⚠ Warning: Issue popping patches, continuing anyway...")
    
    # Apply patches
    series_file = PATCHES_DIR / "series"
    if series_file.exists():
        print("Applying patches...")
        result = run_command(["quilt", "push", "-a"], check=False)
        
        if result.returncode == 0:
            print("✓ All patches applied successfully")
        elif result.returncode == 2:
            print("✓ No patches to apply or already applied")
        else:
            print("⚠ Warning: Some patches may have failed to apply")
            print("Continuing with build anyway...")
    else:
        print("⚠ No patches/series file found")
    
    # Run hooks (if needed for new dependencies)
    print("Running gclient hooks...")
    result = run_command(["gclient", "runhooks"], check=False)
    if result.returncode != 0:
        print("⚠ Warning: gclient hooks had issues, continuing anyway...")
    
    # Rebuild
    print("Rebuilding Chromium with changes...")
    num_jobs = multiprocessing.cpu_count() * 2
    print(f"Building with {num_jobs} parallel jobs...")
    print("Using optimized build configuration...")
    
    cmd = ["ninja", "-C", OUT_DIR, f"-j{num_jobs}", "chrome"]
    run_command(cmd)
    
    binary_path = src_dir / OUT_DIR / "chrome"
    print()
    print("=" * 48)
    print("✓ Rebuild complete!")
    print(f"Binary location: {binary_path}")
    print("=" * 48)
    print()
    print("Next: Run './release.py' to create release package")


if __name__ == "__main__":
    main()
