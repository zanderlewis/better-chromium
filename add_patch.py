#!/usr/bin/env python3
"""
Add new patch to Better Chromium
Usage: ./add_patch.py <patch-file> [patch-name]
"""

import sys
import shutil
from pathlib import Path


def main():
    """Add a patch to the patch series."""
    if len(sys.argv) < 2:
        print("Usage: ./add_patch.py <patch-file> [optional-name]")
        print()
        print("Example:")
        print("  ./add_patch.py /path/to/my.patch")
        print("  ./add_patch.py /path/to/my.patch my-feature")
        sys.exit(1)
    
    script_dir = Path(__file__).parent.resolve()
    patches_dir = script_dir / "patches"
    series_file = patches_dir / "series"
    
    patch_file = Path(sys.argv[1])
    
    # Determine patch name
    if len(sys.argv) >= 3:
        patch_name = sys.argv[2]
    else:
        patch_name = patch_file.name
    
    # Ensure .patch extension
    if not patch_name.endswith(".patch"):
        patch_name += ".patch"
    
    # Check if source patch exists
    if not patch_file.exists():
        print(f"❌ Patch file not found: {patch_file}")
        sys.exit(1)
    
    # Create patches directory if needed
    patches_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy patch to patches directory
    dest_path = patches_dir / patch_name
    shutil.copy2(patch_file, dest_path)
    print(f"✓ Patch copied to: {dest_path}")
    
    # Add to series file
    if series_file.exists():
        with open(series_file, 'r') as f:
            content = f.read()
        
        # Check if patch already in series
        if patch_name in content:
            print(f"⚠ Patch already in series file")
        else:
            with open(series_file, 'a') as f:
                f.write(f"\n# User-added patch\n{patch_name}\n")
            print(f"✓ Patch added to series file")
    else:
        # Create new series file
        with open(series_file, 'w') as f:
            f.write(f"# Quilt patch series\n\n{patch_name}\n")
        print(f"✓ Created series file with patch")
    
    print()
    print("Now run: ./quick_rebuild.py")


if __name__ == "__main__":
    main()
