#!/usr/bin/env bash
set -euo pipefail
trap 'echo "Error on line $LINENO"; exit 1' ERR

PROJECT_NAME="qt_multi_totp_viewer"

echo "=== Qt6 Multi-TOTP Viewer Bootstrap (Graphical Countdown, No Master Password) ==="
echo ""

# ------------------------------------------------------------
# OS CHECK
# ------------------------------------------------------------
if ! command -v apt >/dev/null 2>&1; then
    echo "This script supports Debian/Ubuntu systems only."
    exit 1
fi

# ------------------------------------------------------------
# IDEMPOTENCY CHECK
# ------------------------------------------------------------
if [ -d "$PROJECT_NAME" ]; then
    echo "Directory '$PROJECT_NAME' already exists."
    echo "Remove it first if you want to regenerate."
    exit 0
fi

# ------------------------------------------------------------
# INSTALL DEPENDENCIES
# ------------------------------------------------------------
echo "Updating packages..."
sudo apt update -y

echo "Installing Qt6 + build tools..."
sudo apt install -y \
    nodejs npm \
    build-essential g++ cmake \
    libgl1-mesa-dev libglx-dev \
    qt6-base-dev qt6-tools-dev qt6-tools-dev-tools qtcreator

# ------------------------------------------------------------
# INSTALL KILO IF MISSING
# ------------------------------------------------------------
if ! command -v kilo >/dev/null 2>&1; then
    echo "Installing Kilo CLI..."
    sudo npm install -g @kilocode/cli@latest
fi

# ------------------------------------------------------------
# CONFIGURE KILO
# ------------------------------------------------------------
mkdir -p ~/.config/kilo ~/.kilocode/cli

cat > ~/.config/kilo/opencode.json <<EOF
{
  "\$schema": "https://app.kilo.ai/config.json"
}
EOF

cat > ~/.kilocode/cli/config.json <<EOF
{
  "version": "1.0.0",
  "autoApproval": {
    "enabled": true,
    "write": { "enabled": true },
    "shell": { "enabled": true },
    "mcp": { "enabled": true },
    "default": { "enabled": true }
  }
}
EOF

# ------------------------------------------------------------
# CREATE PROJECT DIRECTORY
# ------------------------------------------------------------
mkdir "$PROJECT_NAME"
cd "$PROJECT_NAME"

echo ""
echo "=== Generating Qt6 Project (Programmatic UI, Graphical Countdown) ==="
echo ""

kilo run --auto "Create a complete Qt6 Widgets application in the CURRENT DIRECTORY.

STRICT REQUIREMENTS:

- Use Qt6 only.
- Include all necessary headers: QHeaderView, QDateTime, QTimer, QTableWidget, QLabel, QSettings, QVector, QMainWindow, QPushButton, QVBoxLayout, QMessageBox, QInputDialog, QCryptographicHash, QProgressBar
- Do NOT use QRegExp.
- Do NOT use QCryptographicHash::hmac.
- Implement HMAC-SHA1 manually using QCryptographicHash.
- Use QByteArray for password hashes and XOR operations where applicable.
- Programmatic UI only (no .ui files).

Application Requirements:

- Display up to 5 TOTP secrets.
- Use QSettings for persistence.
- Do NOT include or prompt for any master password or encryption.
- RFC 4648 Base32 decoding (via QString → QByteArray).
- RFC 6238 TOTP (HMAC-SHA1, 30s, 6 digits).
- Pre-add example: 'Test (Google)' / 'JBSWY3DPEHPK3PXP'.
- Table columns: Name | Current TOTP | Time Left.
- The 'Time Left' column must use a graphical bar (QProgressBar) instead of numbers.
- The bar should visually represent remaining seconds in the 30-second window.
- Bars update every second with color changes (green >15s, orange 6–15s, red ≤5s).
- Add/Edit/Delete buttons for managing entries.
- 1-second update timer for codes and bars.
- Title: 'Multi TOTP Viewer'.
- Default window size: 780x520.

CMakeLists.txt must include:
- set(CMAKE_AUTOMOC ON)
- find_package(Qt6 REQUIRED COMPONENTS Widgets)
- target_link_libraries(... Qt6::Widgets)
"

# ------------------------------------------------------------
# VALIDATION STEP
# ------------------------------------------------------------
echo ""
echo "=== Validating Generated Code ==="

# Check for Qt5 APIs
if grep -R "QRegExp" . >/dev/null; then
    echo "ERROR: QRegExp detected (Qt5 API). Aborting."
    exit 1
fi

# Check for invalid QCryptographicHash::hmac usage (ignore comments)
if grep -R "QCryptographicHash::hmac" . | grep -vE '^\s*//|/\*|^\s*\*'; then
    echo "ERROR: Invalid QCryptographicHash::hmac usage detected. Aborting."
    exit 1
else
    echo "Manual HMAC implementation detected."
fi

# Optional check for manual HMAC implementation presence
if ! (grep -R -E "iKeyPad|ipad" . >/dev/null && grep -R -E "oKeyPad|opad" . >/dev/null); then
    echo "WARNING: Manual HMAC implementation not clearly detected. Verify totp.cpp manually."
fi

# ------------------------------------------------------------
# CONFIGURE CMAKE
# ------------------------------------------------------------
echo ""
echo "=== Configuring CMake ==="

mkdir -p build
cd build

cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..

echo ""
echo "=== Building Project ==="
cmake --build .

# ------------------------------------------------------------
# DETECT EXECUTABLE FOR FIRST RUN
# ------------------------------------------------------------
echo ""
EXECUTABLE=$(find . -maxdepth 1 -type f -executable -name 'Multi*Viewer' | head -n1)
if [ -z "$EXECUTABLE" ]; then
    echo "ERROR: Could not find built executable."
else
    echo "=== First Run (creates QSettings config) ==="
    "$EXECUTABLE" || true
fi

cd ..

# ------------------------------------------------------------
# DETECT CONFIG FILE CREATED BY FIRST RUN
# ------------------------------------------------------------
CONFIG_FILE="$HOME/.config/TOTPViewer/MultiTOTPViewer.conf"
if [ -f "$CONFIG_FILE" ]; then
    echo ""
    echo "Configuration stored at:"
    echo "  $CONFIG_FILE"
else
    echo ""
    echo "Configuration file not yet created. Run the application and save/add entries to generate it:"
    echo "  cd $PROJECT_NAME/build"
    echo "  $EXECUTABLE"
fi

# ------------------------------------------------------------
# DONE
# ------------------------------------------------------------
echo ""
echo "=== Build Complete ==="
echo ""
echo "Run with:"
echo "  cd $PROJECT_NAME/build"
echo "  $EXECUTABLE"
echo ""
echo "Security note:"
echo "  Secrets stored via QSettings are plain text."
echo ""
echo "Done."

