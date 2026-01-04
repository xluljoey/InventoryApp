#!/usr/bin/env python3
"""
Create a clean Windows-compatible copy of the inventory app
and copy it directly to USB drive for Windows build
"""
import os
import shutil
import sys
from pathlib import Path

# USB drive name
USB_NAME = "CCCOMA_X64F"

# Find USB drive
def find_usb_drive():
    """Find the USB drive mount point"""
    possible_paths = [
        f"/media/joey/{USB_NAME}",
        f"/mnt/{USB_NAME}",
        f"/run/media/joey/{USB_NAME}",
        f"/media/{USB_NAME}",
        f"/mnt/{USB_NAME}",
    ]
    
    # Also search in common mount points
    for base in ["/media", "/mnt", "/run/media"]:
        if os.path.exists(base):
            for item in os.listdir(base):
                if USB_NAME.lower() in item.lower() or item.lower() in USB_NAME.lower():
                    possible_paths.append(os.path.join(base, item))
    
    for path in possible_paths:
        if os.path.exists(path) and os.path.isdir(path):
            # Check if it's writable
            test_file = os.path.join(path, ".write_test")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                return path
            except:
                continue
    
    return None

# Project root
PROJECT_ROOT = Path(__file__).parent.absolute()
TARGET_NAME = "inventory_app_WINDOWS"

# Files and directories to include
INCLUDE_PATTERNS = [
    "*.py",
    "*.txt",
    "*.md",
    "*.spec",
    "*.bat",
    "*.ico",
    "*.png",
    "*.db",  # Database file
]

# Directories to include
INCLUDE_DIRS = [
    "core",
    "db",
    "ui",
]

# Files and directories to exclude
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".git",
    ".venv",
    "venv",
    "env",
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cache",
    "*.egg-info",
    ".DS_Store",
    "Thumbs.db",
    "*.log",
    "*.tmp",
]

# Specific files to include (even if they match exclude patterns)
SPECIFIC_FILES = [
    "main.py",
    "requirements.txt",
    "setup.py",
    "micchris.spec",
    "build_windows.bat",
    "generate_icon.py",
    "inventory-management.ico",
    "inventory.db",
    "README.md",
    "QUICK_START.md",
    "WINDOWS_BUILD_GUIDE.md",
]

def should_include(file_path, relative_path):
    """Check if a file should be included"""
    # Check specific files
    if os.path.basename(file_path) in SPECIFIC_FILES:
        return True
    
    # Check exclude patterns
    for pattern in EXCLUDE_PATTERNS:
        if pattern in str(relative_path) or pattern in os.path.basename(file_path):
            return False
    
    # Check if it's in an include directory
    parts = relative_path.parts
    if len(parts) > 0 and parts[0] in INCLUDE_DIRS:
        return True
    
    # Check file extension
    ext = os.path.splitext(file_path)[1]
    if ext in [".py", ".txt", ".md", ".spec", ".bat", ".ico", ".png", ".db"]:
        return True
    
    return False

def create_clean_copy(source_dir, target_dir):
    """Create a clean copy of the project"""
    print(f"📦 Creating clean Windows copy...")
    print(f"   Source: {source_dir}")
    print(f"   Target: {target_dir}")
    print()
    
    # Remove existing target if it exists
    if os.path.exists(target_dir):
        print(f"🗑️  Removing existing copy...")
        shutil.rmtree(target_dir)
    
    # Create target directory
    os.makedirs(target_dir, exist_ok=True)
    
    files_copied = 0
    dirs_copied = 0
    
    # Copy files
    for root, dirs, files in os.walk(source_dir):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if not any(pattern in d for pattern in EXCLUDE_PATTERNS)]
        
        relative_root = os.path.relpath(root, source_dir)
        
        # Skip root directory itself in relative path
        if relative_root == ".":
            relative_root = ""
        
        for file in files:
            source_file = os.path.join(root, file)
            relative_file = Path(relative_root) / file if relative_root else Path(file)
            
            if should_include(source_file, relative_file):
                target_file = os.path.join(target_dir, relative_file)
                target_parent = os.path.dirname(target_file)
                
                # Create parent directories
                os.makedirs(target_parent, exist_ok=True)
                
                # Copy file
                try:
                    shutil.copy2(source_file, target_file)
                    files_copied += 1
                    if files_copied % 10 == 0:
                        print(f"   Copied {files_copied} files...", end='\r')
                except Exception as e:
                    print(f"\n   ⚠️  Warning: Could not copy {relative_file}: {e}")
    
    print(f"\n   ✅ Copied {files_copied} files")
    
    # Create a README for the USB copy
    readme_content = """# Sales & Inventory Management System - Windows Build Package

This is a clean copy of the inventory app, ready for Windows build.

## Quick Start on Windows:

1. **Install Python 3.8+** (if not already installed)
   - Download from: https://www.python.org/downloads/
   - ✅ Make sure to check "Add Python to PATH" during installation

2. **Double-click `build_windows.bat`**
   - The script will automatically:
     - Install all dependencies
     - Generate the application icon
     - Build the Windows executable
     - Create `dist/Sales & Inventory Management System.exe`

3. **Done!** Your executable is ready in the `dist` folder.

## What's Included:

- ✅ All source code (core/, db/, ui/)
- ✅ Build configuration (micchris.spec)
- ✅ Build script (build_windows.bat)
- ✅ Icon generator (generate_icon.py)
- ✅ Requirements file (requirements.txt)
- ✅ Documentation (README.md, WINDOWS_BUILD_GUIDE.md)

## What's NOT Included:

- ❌ Python cache files (__pycache__)
- ❌ Virtual environment (.venv)
- ❌ Build artifacts (build/, dist/)
- ❌ Git files (.git)

## File Size:

This clean copy is ~1-2 MB (vs ~100-300 MB with .venv)

## Need Help?

See WINDOWS_BUILD_GUIDE.md for detailed instructions.
"""
    
    readme_path = os.path.join(target_dir, "USB_README.txt")
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"   📝 Created USB_README.txt")
    print()
    return files_copied

def main():
    """Main function"""
    print("=" * 60)
    print("Sales & Inventory Management System - USB Copy Tool")
    print("=" * 60)
    print()
    
    # Find USB drive
    print(f"🔍 Looking for USB drive: {USB_NAME}...")
    usb_path = find_usb_drive()
    
    if not usb_path:
        print(f"❌ ERROR: USB drive '{USB_NAME}' not found!")
        print()
        print("Please make sure:")
        print("  1. USB drive is inserted")
        print("  2. USB drive is mounted")
        print("  3. USB drive name matches 'CCCOMA_X64F'")
        print()
        print("Trying to find any USB drive...")
        # Try to find any mounted USB
        for base in ["/media/joey", "/mnt", "/run/media/joey"]:
            if os.path.exists(base):
                items = os.listdir(base)
                if items:
                    print(f"   Found drives in {base}: {', '.join(items)}")
        sys.exit(1)
    
    print(f"   ✅ Found USB drive at: {usb_path}")
    print()
    
    # Create clean copy in temporary location first
    temp_target = os.path.join("/tmp", TARGET_NAME)
    print("📦 Step 1: Creating clean copy...")
    files_copied = create_clean_copy(str(PROJECT_ROOT), temp_target)
    
    # Copy to USB
    usb_target = os.path.join(usb_path, TARGET_NAME)
    print(f"📤 Step 2: Copying to USB drive...")
    print(f"   Target: {usb_target}")
    
    # Remove existing copy on USB if it exists
    if os.path.exists(usb_target):
        print(f"   Removing existing copy on USB...")
        try:
            shutil.rmtree(usb_target)
        except Exception as e:
            print(f"   ⚠️  Warning: Could not remove existing copy: {e}")
            print(f"   Trying to continue...")
    
    # Copy to USB
    try:
        shutil.copytree(temp_target, usb_target)
        print(f"   ✅ Successfully copied to USB!")
        print()
        
        # Clean up temp
        shutil.rmtree(temp_target)
        
        # Calculate size
        total_size = 0
        for root, dirs, files in os.walk(usb_target):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                except:
                    pass
        
        size_mb = total_size / (1024 * 1024)
        
        print("=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print()
        print(f"📦 Clean copy created on USB drive:")
        print(f"   Location: {usb_target}")
        print(f"   Files: {files_copied}")
        print(f"   Size: {size_mb:.2f} MB")
        print()
        print("🚀 Next Steps:")
        print("   1. Safely eject USB drive")
        print("   2. Insert into Windows PC")
        print("   3. Navigate to the folder")
        print("   4. Double-click 'build_windows.bat'")
        print()
        
    except Exception as e:
        print(f"❌ ERROR: Could not copy to USB drive: {e}")
        print()
        print(f"   Clean copy is available at: {temp_target}")
        print(f"   You can manually copy it to: {usb_target}")
        sys.exit(1)

if __name__ == "__main__":
    main()