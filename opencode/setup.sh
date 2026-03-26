#!/bin/bash

# =========================================
# Script to install OpenCode on Ubuntu
# =========================================

# Exit immediately if a command exits with a non-zero status
set -e

# Optional: Update package lists
echo "Updating package lists..."
sudo apt update

# Optional: Install curl if not already installed
if ! command -v curl &> /dev/null
then
    echo "curl not found. Installing curl..."
    sudo apt install -y curl
fi

# Download and run OpenCode installer
echo "Installing OpenCode..."
curl -fsSL https://opencode.ai/install | bash

# Installation complete message
echo "OpenCode installation completed!"
