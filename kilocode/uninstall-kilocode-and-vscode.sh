#!/usr/bin/env bash
#
# uninstall-kilocode-and-vscode.sh
# --------------------------------
# Removes VS Code (snap), Kilo Code extension + related data
# Designed as counterpart to setup-kilocode-on-ubuntu-live.sh
# Best run in the same Ubuntu Live USB session or persistent system
#
# 2026 edition — works with Ubuntu 24.04 / 24.10 / 25.xx
#

set -euo pipefail

echo "┌────────────────────────────────────────────────────────────┐"
echo "│      Kilo Code + VS Code COMPLETE removal (snap-based)     │"
echo "│                     THIS WILL DELETE DATA                  │"
echo "└────────────────────────────────────────────────────────────┘"
echo ""

read -p "Are you sure you want to completely remove VS Code, Kilo Code extension and all settings? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# ────────────────────────────────────────────────
# 1. Remove Kilo Code extension (if VS Code is still present)
# ────────────────────────────────────────────────
if command -v code >/dev/null 2>&1; then
    echo "→ Removing Kilo Code extension..."
    code --uninstall-extension kilocode.Kilo-Code || true
    # Just in case — remove any force-installed leftovers
    code --uninstall-extension kilocode.Kilo-Code --force 2>/dev/null || true
else
    echo "→ VS Code CLI not found (code command missing) — skipping extension removal."
fi

# ────────────────────────────────────────────────
# 2. Remove the VS Code snap package (with --purge to avoid snapshots)
# ────────────────────────────────────────────────
if snap list | grep -q "^code "; then
    echo "→ Removing Visual Studio Code snap (with purge)..."
    sudo snap remove code --purge
else
    echo "→ VS Code snap not found."
fi

# ────────────────────────────────────────────────
# 2.1 Remove any existing snapshots for code (if any)
# ────────────────────────────────────────────────
echo "→ Checking and removing any VS Code snap snapshots..."
sudo snap forget $(sudo snap saved | awk '/code/ {print $1}' | xargs) 2>/dev/null || true

# ────────────────────────────────────────────────
# 3. Remove all user data (settings, extensions, cache)
#    Snap-based VS Code stores data under ~/snap/code/
#    But also respects classic snap conventions → remove both common locations
#    Also clean up known trash accumulation issues from VS Code snap bug
# ────────────────────────────────────────────────
echo "→ Removing all VS Code user data, settings, extensions, and trash..."

# Snap-specific data (most important for snap --classic installs)
rm -rf ~/snap/code 2>/dev/null || true

# Standard VS Code data folders (very commonly still used/written even with snap)
rm -rf ~/.vscode          2>/dev/null || true
rm -rf ~/.config/Code      2>/dev/null || true
rm -rf ~/.cache/code       2>/dev/null || true   # sometimes present

# Also remove any lingering global extension cache (rare but possible)
rm -rf ~/.vscode/extensions 2>/dev/null || true

# Clean up per-version trash folders (from known VS Code snap bug)
rm -rf ~/snap/code/[0-9]*/.local/share/Trash 2>/dev/null || true

echo "→ Data folders removed (or already missing)."

# ────────────────────────────────────────────────
# 4. Post-removal checks
# ────────────────────────────────────────────────
echo "→ Running post-removal checks..."

if command -v code >/dev/null 2>&1; then
    echo "⚠ Warning: 'code' command is still available!"
    echo "   This might mean:"
    echo "     - VS Code is also installed via apt/deb (not snap)."
    echo "       → Try: sudo apt remove code && sudo apt autoremove"
    echo "     - Shell cache: Try opening a new terminal or run 'hash -r'"
    echo "     - Desktop entry lingering: Try logging out/in or rebooting the Live session."
    echo "     - If still persists, check 'which code' for the source."
else
    echo "→ 'code' command no longer available — good!"
fi

if snap list | grep -q "^code "; then
    echo "⚠ Warning: VS Code snap still listed! Removal may have failed."
    echo "   Try manually: sudo snap remove code --purge"
else
    echo "→ VS Code snap no longer listed — good!"
fi

# ────────────────────────────────────────────────
# Final message – enhanced explanation
# ────────────────────────────────────────────────
echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                      Removal finished!                             ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "→ Visual Studio Code (snap package) has been completely removed."
echo "→ Kilo Code extension has been removed (if it was present)."
echo "→ All known user settings, cached extensions, workspaces, telemetry,"
echo "  and trash data (from known snap bugs) have been deleted from common locations."
echo ""
echo "Important – the following packages were NOT removed:"
echo "  • git"
echo "  • build-essential"
echo "  • curl"
echo "  • wget"
echo ""
echo "  These are standard development tools that were only installed as"
echo "  helpful companions during setup — and are commonly needed for many"
echo "  other tasks on Ubuntu. They remain on your system unless you"
echo "  manually remove them later (e.g. sudo apt remove git build-essential)."
echo ""
echo "If you ever want to start fresh again, just re-run the original"
echo "setup script — everything should now behave like a clean first-time install."
echo ""
echo "If VS Code is still launchable (e.g., from menu), see the warnings above."
echo "For Ubuntu Live sessions, a reboot (or new boot) often clears lingering icons."
echo ""
echo "Done. Your system is clean of Kilo Code + VS Code snap artifacts."

exit 0
