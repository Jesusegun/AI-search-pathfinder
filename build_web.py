#!/usr/bin/env python3
"""
Build script for pygbag web deployment.

This script builds the pygame project for web and deploys to docs/ folder
for GitHub Pages, while preserving the custom loading screen in docs/index.html.

Usage:
    python build_web.py
"""

import subprocess
import shutil
import sys
from pathlib import Path


def build_web():
    """
    Build the pygame project for web deployment.
    
    Steps:
        1. Run pygbag to generate build/web/ output
        2. Copy all files from build/web/ to docs/ EXCEPT index.html
        3. Preserve the custom loading screen in docs/index.html
    
    Raises:
        subprocess.CalledProcessError: If pygbag build fails.
        FileNotFoundError: If build/web/ directory doesn't exist after build.
    """
    project_root = Path(__file__).parent
    build_web_dir = project_root / "build" / "web"
    docs_dir = project_root / "docs"
    
    print("=" * 60)
    print("[BUILD] Building pygame project for web with pygbag...")
    print("=" * 60)
    
    # Step 1: Run pygbag build
    try:
        subprocess.run(
            [sys.executable, "-m", "pygbag", "--build", str(project_root)],
            check=True,
            cwd=project_root
        )
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] pygbag build failed with exit code {e.returncode}")
        raise
    except FileNotFoundError:
        print("[ERROR] pygbag not found. Install it with: pip install pygbag")
        raise
    
    # Verify build output exists
    if not build_web_dir.exists():
        raise FileNotFoundError(f"Build output not found at {build_web_dir}")
    
    print("\n" + "=" * 60)
    print("[COPY] Copying build files to docs/ (preserving custom index.html)...")
    print("=" * 60)
    
    # Ensure docs directory exists
    docs_dir.mkdir(exist_ok=True)
    
    # Step 2: Copy everything from build/web/ to docs/ EXCEPT index.html
    files_copied = 0
    files_skipped = 0
    
    for item in build_web_dir.iterdir():
        dest_path = docs_dir / item.name
        
        # Skip index.html to preserve custom loading screen
        if item.name == "index.html":
            print(f"  [SKIP] {item.name} (preserving custom loading screen)")
            files_skipped += 1
            continue
        
        try:
            if item.is_dir():
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.copytree(item, dest_path)
                print(f"  [DIR] Copied folder: {item.name}/")
            else:
                shutil.copy2(item, dest_path)
                print(f"  [FILE] Copied: {item.name}")
            files_copied += 1
        except Exception as e:
            print(f"  [WARN] Failed to copy {item.name}: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("[DONE] Build complete!")
    print("=" * 60)
    print(f"   Files/folders copied: {files_copied}")
    print(f"   Files skipped: {files_skipped}")
    print(f"   Output directory: {docs_dir}")
    print("\nNext steps:")
    print("   1. Test locally if needed")
    print("   2. git add docs/")
    print("   3. git commit -m 'Update web build'")
    print("   4. git push")
    print("=" * 60)


if __name__ == "__main__":
    try:
        build_web()
    except Exception as e:
        print(f"\n[FAILED] Build failed: {e}")
        sys.exit(1)
