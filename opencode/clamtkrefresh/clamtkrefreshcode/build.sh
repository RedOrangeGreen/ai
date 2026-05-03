#!/bin/bash
# Build script for clamtkrefresh

set -e

echo "Building clamtkrefresh..."

# Create build directories
mkdir -p build/usr/local/bin
mkdir -p build/usr/share/perl5/ClamTk
mkdir -p build/usr/share/applications
mkdir -p build/usr/share/icons/hicolor/256x256/apps

# Copy executable
cp bin/clamtkrefresh build/usr/local/bin/
chmod +x build/usr/local/bin/clamtkrefresh

# Copy Perl modules
cp lib/ClamTk/*.pm build/usr/share/perl5/ClamTk/

# Copy desktop file (modify for clamtkrefresh)
if [ -f ../clamtk-master/clamtk.desktop ]; then
    sed 's/clamtk/clamtkrefresh/g; s/ClamTk/ClamTk Refresh/g' ../clamtk-master/clamtk.desktop > build/usr/share/applications/clamtkrefresh.desktop
fi

# Copy icon
cp images/clamtk.png build/usr/share/icons/hicolor/256x256/apps/clamtkrefresh.png

echo "Build complete. Files are in the 'build' directory."
echo ""
echo "To install system-wide:"
echo "  sudo cp -r build/* /"
echo ""
echo "To run without installing:"
echo "  PERL5LIB=lib: perl bin/clamtkrefresh"
