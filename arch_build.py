#!/usr/bin/env python3
"""
Better Chromium Build Script
Handles full Chromium build with quilt patch management
Following official Chromium build instructions:
https://chromium.googlesource.com/chromium/src/+/HEAD/docs/linux/build_instructions.md
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import multiprocessing

# Configuration
SCRIPT_DIR = Path(__file__).parent.resolve()
PATCHES_DIR = SCRIPT_DIR / "patches"
CHROMIUM_DIR = SCRIPT_DIR / "chromium-src"
DEPOT_TOOLS_DIR = SCRIPT_DIR / "depot_tools"
OUT_DIR = "out/Default"

# Disable depot_tools auto-update to avoid rate limiting
os.environ["DEPOT_TOOLS_UPDATE"] = "0"


def run_command(cmd, cwd=None, check=True, shell=False):
    """Execute a command and handle errors."""
    if isinstance(cmd, list):
        cmd_str = " ".join(cmd)
    else:
        cmd_str = cmd
        
    print(f"Running: {cmd_str}")
    
    result = subprocess.run(
        cmd,
        cwd=cwd,
        shell=shell,
        check=False,
        capture_output=False,
        text=True
    )
    
    if check and result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    
    return result


def install_dependencies():
    """Install build dependencies for Arch Linux."""
    print("Installing build dependencies...")
    
    packages = [
        "python", "perl", "gcc", "gcc-libs", "bison", "flex", "gperf", "pkgconfig",
        "nss", "alsa-lib", "glib2", "gtk3", "nspr", "freetype2", "cairo", "dbus",
        "xorg-server-xvfb", "xorg-xdpyinfo", "ninja", "git", "libxss", "libxtst",
        "libgnome-keyring", "cups", "libpulse", "ttf-liberation", "xdg-utils",
        "mesa", "libva", "libvdpau", "libxslt", "libexif", "libxrandr", "libxt",
        "libxcb", "libxkbcommon", "libxkbfile", "libxinerama", "libxi", "libxext",
        "libxfixes", "libxdamage", "at-spi2-core", "imagemagick", "quilt"
    ]
    
    cmd = ["sudo", "pacman", "-Syu", "--needed", "--noconfirm"] + packages
    run_command(cmd)
    print("✓ Dependencies installed")


def setup_depot_tools():
    """Clone depot_tools if not present."""
    if not DEPOT_TOOLS_DIR.exists():
        print("Cloning depot_tools...")
        cmd = [
            "git", "clone", "--depth=1",
            "https://chromium.googlesource.com/chromium/tools/depot_tools.git",
            str(DEPOT_TOOLS_DIR)
        ]
        result = run_command(cmd, check=False)
        if result.returncode != 0:
            print("❌ Failed to clone depot_tools")
            sys.exit(1)
        print("✓ depot_tools cloned successfully")
    else:
        print("✓ depot_tools already exists")
    
    # Add depot_tools to PATH
    os.environ["PATH"] = f"{DEPOT_TOOLS_DIR}:{os.environ['PATH']}"


def fetch_chromium():
    """Fetch Chromium source code."""
    CHROMIUM_DIR.mkdir(parents=True, exist_ok=True)
    
    src_dir = CHROMIUM_DIR / "src"
    if not src_dir.exists():
        print("Fetching Chromium source for version 144.0.7521.1 (shallow clone)...")
        print("This will take a while but only downloads the specific version...")
        
        # Create .gclient file for gclient sync
        os.chdir(CHROMIUM_DIR)
        gclient_content = """solutions = [
  {
    "name": "src",
    "url": "https://chromium.googlesource.com/chromium/src.git",
    "managed": False,
    "custom_deps": {},
    "custom_vars": {},
  },
]
target_os = ["linux"]
"""
        with open(".gclient", "w") as f:
            f.write(gclient_content)
        
        # Shallow clone just the specific tag
        src_dir.mkdir(parents=True, exist_ok=True)
        os.chdir(src_dir)
        print("Cloning Chromium at tag 144.0.7521.1 (shallow)...")
        run_command([
            "git", "clone", 
            "--depth=1", 
            "--branch", "144.0.7521.1",
            "--single-branch",
            "https://chromium.googlesource.com/chromium/src.git",
            "."
        ])
        print("✓ Chromium source cloned (shallow)")
        
        # Sync dependencies for this specific version
        print("Syncing dependencies for version 144.0.7521.1...")
        os.chdir(CHROMIUM_DIR)
        run_command(["gclient", "sync", "--no-history", "-D"])
    else:
        print("✓ Chromium source already exists")
        os.chdir(src_dir)


def apply_patches_with_quilt():
    """Apply patches using quilt."""
    src_dir = CHROMIUM_DIR / "src"
    os.chdir(src_dir)
    
    # Set up quilt environment
    os.environ["QUILT_PATCHES"] = str(PATCHES_DIR)
    
    # Check if patches exist
    series_file = PATCHES_DIR / "series"
    if not series_file.exists():
        print("⚠ No patches/series file found, skipping patch application")
        return
    
    # Check if any patches have been applied already
    result = run_command(["quilt", "applied"], check=False)
    if result.returncode == 0:
        print("Patches already applied, popping all...")
        run_command(["quilt", "pop", "-a"], check=False)
    
    # Apply all patches
    print("Applying patches with quilt...")
    result = run_command(["quilt", "push", "-a"], check=False)
    
    if result.returncode == 0:
        print("✓ All patches applied successfully")
    elif result.returncode == 2:
        print("✓ Some patches already applied or no patches to apply")
    else:
        print("⚠ Warning: Some patches may have failed to apply")


def run_gclient_hooks():
    """Run gclient hooks."""
    print("Running gclient hooks...")
    src_dir = CHROMIUM_DIR / "src"
    os.chdir(src_dir)
    run_command(["gclient", "runhooks"])
    print("✓ Hooks completed")


def ensure_depot_tools_ready():
    """Ensure depot_tools is fully initialized."""
    print("Ensuring depot_tools is initialized...")
    depot_tools_bootstrap = DEPOT_TOOLS_DIR / "ensure_bootstrap"
    if depot_tools_bootstrap.exists():
        os.chdir(DEPOT_TOOLS_DIR)
        run_command([str(depot_tools_bootstrap)])
        print("✓ depot_tools initialized")


def configure_build():
    """Configure build with gn."""
    print("Configuring build with optimized flags...")
    src_dir = CHROMIUM_DIR / "src"
    os.chdir(src_dir)
    
    build_args = [
        # Build type
        "is_debug=false",
        
        # Optimization
        "is_component_build=false",
        "symbol_level=0",
        "blink_symbol_level=0",
        "enable_nacl=false",
        
        # Linker optimization
        "use_mold=true",
        
        # Security (disable for faster builds)
        "is_cfi=false",
        
        # Disable unnecessary features
        "enable_resource_allowlist_generation=false",
        "enable_precompiled_headers=false",
        
        # Compiler optimizations
        "optimize_webui=true",
        "enable_iterator_debugging=false",
        
        # Remove dev/test features
        "remove_webcore_debug_symbols=true",
        "enable_reading_list=false",
        "enable_service_discovery=false",
        "enable_hangout_services_extension=false",
        
        # Performance
        "use_remoteexec=false",
        "enable_print_preview=true",
        
        # JavaScript optimization
        "v8_symbol_level=0",
        "v8_enable_debugging_features=false",
    ]
    
    args_str = " ".join(build_args)
    cmd = ["gn", "gen", OUT_DIR, f"--args={args_str}"]
    run_command(cmd)
    print("✓ Build configured")


def build_chromium():
    """Build Chromium with ninja."""
    print("Building Chromium...")
    src_dir = CHROMIUM_DIR / "src"
    os.chdir(src_dir)

    cpu_count = multiprocessing.cpu_count()

    num_jobs = cpu_count * 2
    
    print(f"Building with {num_jobs} parallel jobs...")
    
    cmd = ["ninja", "-C", OUT_DIR, f"-j{num_jobs}", "chrome"]
    run_command(cmd)
    
    binary_path = src_dir / OUT_DIR / "chrome"
    print()
    print("=" * 48)
    print("Chromium build complete!")
    print(f"Binary location: {binary_path}")
    print(f"Run with: {binary_path}")
    print("=" * 48)


def main():
    """Main build orchestration."""
    print("=" * 48)
    print("Better Chromium - Full Build")
    print("=" * 48)
    print()
    
    install_dependencies()
    setup_depot_tools()
    fetch_chromium()
    apply_patches_with_quilt()
    run_gclient_hooks()
    ensure_depot_tools_ready()
    configure_build()
    build_chromium()


if __name__ == "__main__":
    main()
