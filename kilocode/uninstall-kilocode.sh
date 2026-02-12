#!/usr/bin/env bash
set -euo pipefail

echo "=== Resetting Kilo Code extension in VS Code (Ubuntu) ==="
echo "Make sure ALL VS Code windows are CLOSED before continuing."
echo "Press Enter to proceed (or Ctrl+C to cancel)"
read -r

EXTENSION_ID="kilocode.Kilo-Code"

echo "1. Attempting clean uninstall via VS Code CLI..."
code --uninstall-extension "$EXTENSION_ID" 2>/dev/null || echo "  (Extension not found or already uninstalled — continuing)"

echo "2. Removing extension folder(s)..."
rm -rf ~/.vscode/extensions/kilocode* ~/.vscode/extensions/*kilo* 2>/dev/null || true

echo "3. Removing Kilo Code global storage..."
rm -rf ~/.config/Code/User/globalStorage/kilocode* ~/.config/Code/User/globalStorage/*kilo* 2>/dev/null || true

echo "4. Resetting shared global state DB (removes onboarding flags etc.)..."
rm -f ~/.config/Code/User/globalStorage/state.vscdb* 2>/dev/null || true

echo "5. Clearing extension caches (helps avoid invalid/faded state)..."
rm -rf ~/.config/Code/CachedExtensions/*kilo* ~/.config/Code/CachedData/* 2>/dev/null || true
rm -f ~/.vscode/extensions/.obsolete 2>/dev/null || true

echo ""
echo "=== Reset complete ==="
