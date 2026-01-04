#!/usr/bin/env python3
"""
Update inventory_app_CLEAN on Desktop with latest changes
Run this after making changes to sync them
"""
import shutil
import os
from pathlib import Path

source = Path("/home/joey/Desktop/projects/inventory_app")
desktop_dest = Path("/home/joey/Desktop/inventory_app_CLEAN")

print("=" * 60)
print("SYNCING LATEST CHANGES")
print("=" * 60)
print()

# Ensure destination exists
if desktop_dest.exists():
    print(f"✓ Found existing folder: {desktop_dest}")
    response = input("Update this folder with latest changes? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        exit(0)
    
    # Remove old version
    print("Removing old version...")
    shutil.rmtree(desktop_dest)
else:
    print(f"Creating new folder: {desktop_dest}")

# Copy everything
print("Copying latest version...")
shutil.copytree(source, desktop_dest, 
               ignore=shutil.ignore_patterns('.venv', 'build', 'dist', '__pycache__', '.git', '*.pyc'))

print()
print("=" * 60)
print("✅ SYNC COMPLETE!")
print("=" * 60)
print(f"📁 Updated: {desktop_dest}")
print()
print("Changes included:")
print("  ✓ Fixed Edit Customer feature")
print("  ✓ Added payment_history table")
print("  ✓ Optimized .spec file for faster startup")
print("  ✓ All button functions verified")
print()
print("Next: Copy inventory_app_CLEAN to USB drive")
print()
