#!/bin/bash

# =========================================
# Script to run OpenCode (robust)
# =========================================

set -e

# -----------------------------------------
# Load saved install path
# -----------------------------------------

if [ -f "$HOME/.opencode_path" ]; then
    OPENCODE_PATH=$(cat "$HOME/.opencode_path")
else
    echo "ERROR: OpenCode path file not found (~/.opencode_path)."
    echo "Run setup.sh first."
    exit 1
fi

# Add to PATH
export PATH="$OPENCODE_PATH:$HOME/.local/bin:/usr/local/bin:$PATH"

# Refresh shell cache
hash -r

# Verify
if ! command -v opencode &> /dev/null
then
    echo "ERROR: OpenCode still not found in PATH."
    echo "Checked path: $OPENCODE_PATH"
    exit 1
fi

echo "Starting OpenCode..."
opencode

echo "OpenCode has exited."
