#!/bin/bash

# =========================================
# Script to run OpenCode
# =========================================

# Exit immediately if a command exits with a non-zero status
set -e

# Check if OpenCode is installed
if ! command -v opencode &> /dev/null
then
    echo "OpenCode is not installed. Please install it first."
    exit 1
fi

# Run OpenCode
echo "Starting OpenCode..."
opencode

# Optional: message after execution
echo "OpenCode has exited."
