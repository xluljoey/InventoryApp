#!/usr/bin/env python3
"""
Quick script to copy project to USB - CLEANS ALL unnecessary files first
"""
import os
import shutil
from pathlib import Path

project = Path("/home/joey/Desktop/projects/inventory_app")

# Files to delete (cleanup)
delete_files = [
    "QUICK_START.md",
    "WINDOWS_BUILD_GUIDE.md",
    "ALL_FIXED.txt",
    "ALL_FIXES_COMPLETE.txt",
    "FIXES_APPLIED.txt",
    "LATEST_FIXES.txt",
    "SPACING_FIXED.txt",
    "create_clean_copy.py",
    "cleanup_project.py",
    "do_cleanup_now.py",
    "check_size.py",
    "quick_actions.py",
    "setup_and_build.py",
]

print("🧹 Cleaning up documentation files...")
for f in delete_files:
    fp = project / f
    if fp.exists():
        os.remove(fp)
        print(f"  ✓ Deleted {f}")

# Clean directories
dirs_to_clean = ["build", "dist", "__pycache__"]
for d in dirs_to_clean:
    dp = project / d
    if dp.exists():
        shutil.rmtree(dp)
        print(f"  ✓ Cleaned {d}/")

# Clean pycache in subdirs
for root, dirs, files in os.walk(project):
    if "__pycache__" in dirs:
        shutil.rmtree(os.path.join(root, "__pycache__"))

print("\n✅ Project cleaned!")
print(f"📁 Clean project at: {project}")
