#!/usr/bin/env bash
#
# setup-vscode-and-kilocode.sh
# ----------------------------
# Installs VS Code (snap), Kilo Code extension + useful basics
# Best run in Ubuntu Live USB session
#
# 2026 edition — works with Ubuntu 24.04 / 24.10 / 25.xx
#

set -euo pipefail

echo "┌──────────────────────────────────────────────────────┐"
echo "│         VS Code + Kilo Code setup for Ubuntu         │"
echo "│             (snap-based • 2026 friendly)             │"
echo "└──────────────────────────────────────────────────────┘"
echo ""

# ────────────────────────────────────────────────
# 1. Make sure snapd is present
# ────────────────────────────────────────────────
if ! command -v snap >/dev/null 2>&1; then
    echo "→ Installing snapd ..."
    sudo apt update
    sudo apt install -y snapd
    # Give snapd a moment to initialize socket & paths
    sleep 5
else
    echo "→ snapd already installed."
fi

# Refresh core snap (helps avoid classic confinement issues)
echo "→ Refreshing snap core..."
sudo snap refresh core || true

# ────────────────────────────────────────────────
# 2. Install Visual Studio Code (official snap)
# ────────────────────────────────────────────────
if snap list | grep -q "^code "; then
    echo "→ VS Code snap already installed."
else
    echo "→ Installing Visual Studio Code (snap)..."
    sudo snap install code --classic
fi

# ────────────────────────────────────────────────
# 3. Install Kilo Code extension
# Publisher: kilocode    ID: kilocode.Kilo-Code
# ────────────────────────────────────────────────
echo "→ Installing Kilo Code extension..."
code --install-extension kilocode.Kilo-Code || {
    echo "⚠  Extension install failed. Trying force-refresh method..."
    sudo snap refresh code
    code --install-extension kilocode.Kilo-Code --force
}

# ────────────────────────────────────────────────
# 4. Optional but strongly recommended companions
# ────────────────────────────────────────────────
echo "→ Installing git + basic build tools (very useful with Kilo)..."
sudo apt update
sudo apt install -y git build-essential curl wget

# ────────────────────────────────────────────────
# Final instructions
# ────────────────────────────────────────────────
echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║                  Setup finished!                   ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Launch VS Code:     code"
echo "                         (or search 'Visual Studio Code' in menu)"
echo ""

exit 0
