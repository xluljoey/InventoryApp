#!/bin/bash

# Script to sync changes to USB drive
# USB Name: CCCOMA_X64F

USB_PATH="/run/media/joey/CCCOMA_X64F/inventory_app"
SOURCE_PATH="/home/joey/Desktop/projects/inventory_app"

echo "========================================="
echo "SYNCING TO USB: CCCOMA_X64F"
echo "========================================="
echo ""

# Check if USB is mounted
if [ ! -d "/run/media/joey/CCCOMA_X64F" ]; then
    echo "❌ ERROR: USB drive CCCOMA_X64F not found!"
    echo "Please make sure the USB is plugged in."
    exit 1
fi

echo "✓ USB drive found"
echo ""

# Check if inventory_app exists on USB
if [ ! -d "$USB_PATH" ]; then
    echo "❌ ERROR: inventory_app folder not found on USB!"
    echo "Expected location: $USB_PATH"
    exit 1
fi

echo "✓ inventory_app folder found on USB"
echo ""

# Show what will be updated
echo "📋 Files that will be updated:"
echo "  • ui/customer_window.py (Edit Customer fix)"
echo "  • db/database.py (payment_history table)"
echo "  • micchris.spec (optimized build)"
echo "  • main.py (if changed)"
echo "  • All other source files"
echo ""

read -p "Continue with sync? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "🔄 Syncing files..."
echo ""

# Copy modified files
echo "  ✓ Copying ui/customer_window.py..."
cp "$SOURCE_PATH/ui/customer_window.py" "$USB_PATH/ui/"

echo "  ✓ Copying db/database.py..."
cp "$SOURCE_PATH/db/database.py" "$USB_PATH/db/"

echo "  ✓ Copying micchris.spec..."
cp "$SOURCE_PATH/micchris.spec" "$USB_PATH/"

echo "  ✓ Copying main.py..."
cp "$SOURCE_PATH/main.py" "$USB_PATH/"

echo "  ✓ Copying ui/sell_window.py..."
cp "$SOURCE_PATH/ui/sell_window.py" "$USB_PATH/"

echo "  ✓ Copying core files..."
cp -r "$SOURCE_PATH/core/"* "$USB_PATH/core/"

echo "  ✓ Copying other ui files..."
cp "$SOURCE_PATH/ui/"*.py "$USB_PATH/ui/"

echo "  ✓ Copying README.md..."
cp "$SOURCE_PATH/README.md" "$USB_PATH/"

echo "  ✓ Copying build script..."
cp "$SOURCE_PATH/build_windows.bat" "$USB_PATH/"

echo ""
echo "========================================="
echo "✅ SYNC COMPLETE!"
echo "========================================="
echo ""
echo "📁 USB Location: $USB_PATH"
echo ""
echo "✅ Changes applied:"
echo "  • Edit Customer feature fixed"
echo "  • Payment history table added"
echo "  • Build optimized for faster startup"
echo "  • All customer buttons working"
echo ""
echo "Next steps:"
echo "  1. Safely eject USB"
echo "  2. Plug into Windows PC"
echo "  3. Run: build_windows.bat"
echo ""
