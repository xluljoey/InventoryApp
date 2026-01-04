#!/usr/bin/env python3
"""
Sync all changes to USB drive CCCOMA_X64F
"""
import shutil
import os
from pathlib import Path

USB_PATH = Path("/run/media/joey/CCCOMA_X64F/inventory_app")
SOURCE_PATH = Path("/home/joey/Desktop/projects/inventory_app")

print("=" * 60)
print("SYNCING TO USB: CCCOMA_X64F")
print("=" * 60)
print()

# Check if USB is mounted
if not USB_PATH.parent.exists():
    print("❌ ERROR: USB drive CCCOMA_X64F not found!")
    print("Please make sure the USB is plugged in.")
    print()
    print("Expected location: /run/media/joey/CCCOMA_X64F")
    exit(1)

print("✓ USB drive found")

# Check if inventory_app exists on USB
if not USB_PATH.exists():
    print("❌ ERROR: inventory_app folder not found on USB!")
    print(f"Expected location: {USB_PATH}")
    exit(1)

print("✓ inventory_app folder found on USB")
print()

# Show what will be updated
print("📋 Files that will be updated:")
print("  • ui/customer_window.py (Edit Customer fix)")
print("  • db/database.py (payment_history table)")
print("  • micchris.spec (optimized build)")
print("  • ui/sell_window.py (spacing fixes)")
print("  • main.py (alert banner fix)")
print("  • All other source files")
print()

response = input("Continue with sync? (y/n): ")
if response.lower() != 'y':
    print("Cancelled.")
    exit(0)

print()
print("🔄 Syncing files...")
print()

# Critical files to copy
files_to_copy = [
    ("ui/customer_window.py", "Edit Customer fix"),
    ("db/database.py", "payment_history table"),
    ("micchris.spec", "optimized build"),
    ("main.py", "alert banner fix"),
    ("ui/sell_window.py", "spacing fixes"),
    ("README.md", "documentation"),
    ("build_windows.bat", "build script"),
    ("requirements.txt", "dependencies"),
    ("inventory-management.ico", "icon"),
]

for file_path, description in files_to_copy:
    src = SOURCE_PATH / file_path
    dst = USB_PATH / file_path
    if src.exists():
        # Ensure destination directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  ✓ {file_path} ({description})")
    else:
        print(f"  ⚠ {file_path} not found, skipping")

# Copy all ui files
print()
print("  ✓ Copying all UI files...")
ui_src = SOURCE_PATH / "ui"
ui_dst = USB_PATH / "ui"
for py_file in ui_src.glob("*.py"):
    shutil.copy2(py_file, ui_dst / py_file.name)

# Copy all core files
print("  ✓ Copying all core files...")
core_src = SOURCE_PATH / "core"
core_dst = USB_PATH / "core"
for py_file in core_src.glob("*.py"):
    shutil.copy2(py_file, core_dst / py_file.name)

# Copy all db files
print("  ✓ Copying all db files...")
db_src = SOURCE_PATH / "db"
db_dst = USB_PATH / "db"
for py_file in db_src.glob("*.py"):
    shutil.copy2(py_file, db_dst / py_file.name)

print()
print("=" * 60)
print("✅ SYNC COMPLETE!")
print("=" * 60)
print()
print(f"📁 USB Location: {USB_PATH}")
print()
print("✅ Changes applied:")
print("  • Edit Customer feature fixed")
print("  • Payment history table added")
print("  • Build optimized for faster startup")
print("  • All customer buttons working")
print("  • Sell window spacing optimized")
print("  • Alert banner fixed")
print()
print("Next steps:")
print("  1. Safely eject USB")
print("  2. Plug into Windows PC")
print("  3. Run: build_windows.bat")
print()