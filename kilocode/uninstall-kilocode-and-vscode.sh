#!/usr/bin/env bash
set -euo pipefail

EXT_ID="kilocode.kilo-code"
PATTERN="kilocode"

echo "=== Step 0: Close all VS Code windows before proceeding ==="
read -rp "Press ENTER to continue if VS Code is closed..."

# 1) Remove the KiloCode extension and its traces
if command -v code >/dev/null 2>&1; then
  echo "[1] Uninstalling VS Code extension: $EXT_ID (if present)..."
  code --uninstall-extension "$EXT_ID" --force || true
else
  echo "[1] 'code' CLI not found; skipping direct extension uninstall."
fi

EXT_ROOT="$HOME/.vscode/extensions"
if [ -d "$EXT_ROOT" ]; then
  echo "[1] Removing extension folders under $EXT_ROOT matching $PATTERN ..."
  find "$EXT_ROOT" -maxdepth 1 -mindepth 1 -type d -iname "*$PATTERN*" -print0 |
    xargs -0r rm -rf --
fi

CODE_CONF="$HOME/.config/Code"
USER_DIR="$CODE_CONF/User"
SETTINGS="$USER_DIR/settings.json"

if [ -f "$SETTINGS" ]; then
  echo "[1] Cleaning settings mentioning $PATTERN in $SETTINGS ..."
  backup="$SETTINGS.bak.$PATTERN-$(date +%Y%m%d%H%M%S)"
  cp "$SETTINGS" "$backup"
  grep -vi "$PATTERN" "$backup" > "$SETTINGS" || true
  echo "[1] Settings backup at: $backup"
fi

for p in "$USER_DIR/workspaceStorage" \
         "$USER_DIR/globalStorage" \
         "$CODE_CONF/CachedExtensionVSIXs"
do
  if [ -d "$p" ]; then
    echo "[1] Removing cached data in $p containing $PATTERN ..."
    find "$p" -iname "*$PATTERN*" -print0 | xargs -0r rm -rf --
  fi
done

# 2) Remove all VS Code user data (config + extensions)
echo "[2] Removing all VS Code user data for a clean system..."

rm -rf "$HOME/.vscode"
rm -rf "$HOME/.config/Code"

# 3) Uninstall VS Code itself (apt and snap variants)

echo "[3] Attempting to remove VS Code installed via APT (if present)..."
if command -v apt >/dev/null 2>&1; then
  # This will fail harmlessly if 'code' is not installed via apt
  sudo apt remove --purge -y code || true
  sudo apt autoremove -y || true
fi

echo "[3] Attempting to remove VS Code installed via Snap (if present)..."
if command -v snap >/dev/null 2>&1; then
  # This will fail harmlessly if 'code' is not installed via snap
  sudo snap remove code || true
fi

echo
echo "=== All done ==="
echo "- KiloCode extension data removed (as far as detectable)."
echo "- VS Code user data wiped (~/.vscode and ~/.config/Code)."
echo "- VS Code package removed via apt/snap if it was installed that way."
echo "You now have a system without VS Code or the KiloCode extension."
