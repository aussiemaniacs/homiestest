#!/bin/bash

# MovieStream Kodi Addon - Packaging Script
# This script creates a ZIP file ready for Kodi installation

echo "MovieStream Kodi Addon - Packaging Script"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "addon.xml" ]; then
    echo "❌ Error: addon.xml not found. Please run this script from the addon root directory."
    exit 1
fi

# Create package directory
PACKAGE_DIR="plugin.video.moviestream"
ZIP_FILE="plugin.video.moviestream-1.0.0.zip"

echo "📦 Creating package directory..."
mkdir -p "$PACKAGE_DIR"

# Copy addon files
echo "📋 Copying addon files..."
cp addon.xml "$PACKAGE_DIR/"
cp main.py "$PACKAGE_DIR/"
cp icon.png "$PACKAGE_DIR/"
cp fanart.jpg "$PACKAGE_DIR/"

# Copy resources
echo "📁 Copying resources..."
cp -r resources "$PACKAGE_DIR/"

# Copy documentation
echo "📄 Copying documentation..."
cp README.md "$PACKAGE_DIR/"
cp INSTALL.md "$PACKAGE_DIR/"
cp LICENSE "$PACKAGE_DIR/"

# Copy sample JSON files (optional for users)
echo "📊 Copying sample JSON files..."
cp -r sample_json_files "$PACKAGE_DIR/"

# Create ZIP file
echo "🗜️ Creating ZIP file..."
if command -v zip &> /dev/null; then
    zip -r "$ZIP_FILE" "$PACKAGE_DIR"
    echo "✅ Package created: $ZIP_FILE"
else
    echo "⚠️ ZIP command not found. Please manually zip the '$PACKAGE_DIR' directory."
fi

# Cleanup
echo "🧹 Cleaning up..."
rm -rf "$PACKAGE_DIR"

echo ""
echo "🎉 Packaging complete!"
echo ""
echo "Installation Instructions:"
echo "1. Copy $ZIP_FILE to your Kodi device"
echo "2. In Kodi: Add-ons → Install from zip file"
echo "3. Select the ZIP file and install"
echo "4. Configure the addon settings"
echo ""
echo "GitHub Setup:"
echo "1. Upload sample_json_files/* to your GitHub repository"
echo "2. Set GitHub Repository URL in addon settings to:"
echo "   https://raw.githubusercontent.com/yourusername/your-repo/main/"
echo ""
echo "Happy streaming! 🎬"