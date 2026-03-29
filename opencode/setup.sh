#!/bin/bash

# =========================================
# Script to install OpenCode (robust)
# =========================================

set -e

echo "Updating package lists..."
sudo apt update

# Ensure curl exists
if ! command -v curl &> /dev/null
then
    echo "Installing curl..."
    sudo apt install -y curl
fi

echo "Downloading OpenCode installer..."
curl -fsSL https://opencode.ai/install -o install.sh

echo "Running installer..."
bash install.sh

# -----------------------------------------
# Detect where opencode was installed
# -----------------------------------------

echo "Detecting OpenCode installation path..."

OPENCODE_PATH=""

# Common locations to check
for dir in "$HOME/.opencode/bin" "$HOME/.local/bin" "/usr/local/bin"
do
    if [ -x "$dir/opencode" ]; then
        OPENCODE_PATH="$dir"
        break
    fi
done

# Fallback: search if not found
if [ -z "$OPENCODE_PATH" ]; then
    FOUND=$(find "$HOME" -name opencode -type f -executable 2>/dev/null | head -n 1 || true)
    if [ -n "$FOUND" ]; then
        OPENCODE_PATH=$(dirname "$FOUND")
    fi
fi

# Fail if still not found
if [ -z "$OPENCODE_PATH" ]; then
    echo "ERROR: Could not find opencode after installation."
    exit 1
fi

echo "OpenCode found in: $OPENCODE_PATH"

# Save path for run script
echo "$OPENCODE_PATH" > "$HOME/.opencode_path"

echo "Installation complete!"
echo "Saved path to ~/.opencode_path"
