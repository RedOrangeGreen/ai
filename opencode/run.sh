#!/bin/bash

# =========================================
# Script to run OpenCode
# =========================================

# Exit immediately if a command exits with a non-zero status
set -e

# Load user environment (ensures PATH includes opencode)
if [ -f "$HOME/.bashrc" ]; then
    source "$HOME/.bashrc"
fi

# Optional: also include common local bin path (extra safety)
export PATH="$HOME/.local/bin:$PATH"

# Debug (optional - uncomment if needed)
# echo "PATH=$PATH"
# command -v opencode || true

# Check if OpenCode is installed
if ! command -v opencode &> /dev/null
then
    echo "OpenCode is not installed or not in PATH."
    exit 1
fi

# Run OpenCode
echo "Starting OpenCode..."
opencode

# Optional: message after execution
echo "OpenCode has exited."
