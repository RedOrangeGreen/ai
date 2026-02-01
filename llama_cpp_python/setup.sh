#!/usr/bin/env bash
set -e

PYTHON=python3
ENV_DIR="$HOME/py-ai-env"
SCRIPT_NAME="my_wikipedia_script.py"
MODEL_DIR="$HOME/Downloads"
MODEL_URL="https://huggingface.co/unsloth/gemma-3-1b-it-GGUF/resolve/main/gemma-3-1b-it-Q8_0.gguf"
MODEL_FILE="gemma-3-1b-it-Q8_0.gguf"

echo "=== AI Wikipedia Research Environment Setup + Launcher ==="
echo "Using Python: $PYTHON"

# 1. Install curl if missing (Ubuntu/Debian)
if ! command -v curl >/dev/null 2>&1; then
  echo "Installing curl..."
  sudo apt update
  sudo apt install -y curl
fi

# 2. Install dependencies in SMALLER GROUPS
echo "Installing Python build tools..."
sudo apt install -y python3-venv python3-dev python3-pip build-essential

echo "Installing Qt/PySide6 dependencies (group 1)..."
sudo apt install -y libxcb-cursor0 libxkbcommon-x11-0 libxcb-xinerama0 libxcb-keysyms1 libxcb-shape0 libxcb-shm0

echo "Installing Qt/PySide6 dependencies (group 2)..."
sudo apt install -y libxcb-render-util0 libxcb-icccm4 libxcb-image0 libxcb-randr0 libx11-xcb1 libgl1 libfontconfig1

echo "Installing Qt/PySide6 dependencies (group 3)..."
sudo apt install -y libdbus-1-3 libxcb-util1 libxrandr2 libxss1 libxcursor1 libxi6 libxrender1 libxtst6

# 3. Create virtual environment
if [ ! -d "$ENV_DIR" ]; then
  echo "Creating virtual environment at $ENV_DIR ..."
  "$PYTHON" -m venv "$ENV_DIR"
fi

# 4. Activate environment
echo "Activating virtual environment..."
source "$ENV_DIR/bin/activate"

# 5. Upgrade pip and install core packages
echo "Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel

echo "Installing packages..."
python -m pip install "wikipedia-api" PySide6 "llama-cpp-python[server]"

# 6. Download model to ~/Downloads (~1.2GB) - FIXED curl error
mkdir -p "$MODEL_DIR"
MODEL_PATH="$MODEL_DIR/$MODEL_FILE"

if [ ! -f "$MODEL_PATH" ]; then
  echo "Creating temporary directory for download..."
  TEMP_DIR=$(mktemp -d)
  TEMP_FILE="$TEMP_DIR/$MODEL_FILE"
  
  echo "Downloading Gemma-3-1B-IT model (~1.2GB) to temporary location..."
  if curl -L "$MODEL_URL" -o "$TEMP_FILE" --progress-bar --retry 3 --retry-delay 5; then
    echo "Moving model to final location..."
    mv "$TEMP_FILE" "$MODEL_PATH"
    rm -rf "$TEMP_DIR"
    echo "✅ Model downloaded to $MODEL_PATH!"
  else
    echo "❌ Download failed. Cleaning up..."
    rm -rf "$TEMP_DIR"
    exit 1
  fi
else
  echo "✅ Model already exists at $MODEL_PATH"
fi

# 7. Create Python script if missing
if [ ! -f "$SCRIPT_NAME" ]; then
  echo "Creating $SCRIPT_NAME with Wikipedia + AI GUI..."
  cat > "$SCRIPT_NAME" << 'EOF'
[PASTE THE FULL PYTHON SCRIPT HERE - the enhanced Wikipedia + LLM version from previous response]
EOF
  chmod +x "$SCRIPT_NAME"
  echo "✅ Created $SCRIPT_NAME"
fi

# 8. Set Qt environment variables
export QT_QPA_PLATFORM=xcb
export QT_QPA_PLATFORMTHEME=qt5ct

echo ""
echo "✅ Setup complete!"
echo "Virtual environment: $ENV_DIR"
echo "Model location: $MODEL_PATH"
echo "Python script: $SCRIPT_NAME"
echo ""

echo "🚀 LAUNCHING Wikipedia + AI GUI..."
echo "Press Ctrl+C to stop"
echo ""

# 9. LAUNCH the Python application (stays running)
cd "$(dirname "$0")"
source "$ENV_DIR/bin/activate"
QT_QPA_PLATFORM=xcb python "$SCRIPT_NAME"

echo ""
echo "✅ GUI closed. Environment ready for manual use."
echo "To run again: source \"$ENV_DIR/bin/activate\" && QT_QPA_PLATFORM=xcb python $SCRIPT_NAME"
