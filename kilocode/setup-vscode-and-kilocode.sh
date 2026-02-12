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

# ────────────────────────────────────────────────
# 1b. Refresh core snap (if present)
# ────────────────────────────────────────────────
if snap list 2>/dev/null | grep -q '^core '; then
    echo "→ Refreshing snap core..."
    sudo snap refresh core >/dev/null 2>&1 || true
else
    echo "→ 'core' snap not installed; skipping core refresh."
fi

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
if ! command -v code >/dev/null 2>&1; then
    echo "⚠  VS Code CLI not available yet."
    echo "   Tip: Start VS Code once, close it, then re-run this script"
else
    if ! code --install-extension kilocode.Kilo-Code >/dev/null 2>&1; then
        echo "⚠  Extension install failed. Trying force-refresh method..."
        sudo snap refresh code >/dev/null 2>&1 || true
        if ! code --install-extension kilocode.Kilo-Code --force >/dev/null 2>&1; then
            echo "⚠  Extension install still failing; please install from VS Code UI:"
            echo "   1. Open VS Code"
            echo "   2. Go to Extensions"
            echo "   3. Search for 'Kilo Code' (kilocode.Kilo-Code)"
        fi
    fi
fi

# ────────────────────────────────────────────────
# 4. Optional but strongly recommended companions
# ────────────────────────────────────────────────
echo "→ Installing git + basic build tools (very useful with Kilo)..."
sudo apt update
sudo apt install -y git build-essential curl wget

# ────────────────────────────────────────────────
# 5. Quick snap / VS Code health check
# ────────────────────────────────────────────────
echo ""
echo "→ Snap info summary:"
snap version || true
echo ""
echo "→ VS Code snap status:"
snap list code 2>/dev/null || echo "   VS Code snap not listed (install may have failed)."

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
echo "  2. If 'code' is not found, log out and back in, or reboot."
echo ""

exit 0
