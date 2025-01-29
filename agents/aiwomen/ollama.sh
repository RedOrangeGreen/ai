#!/bin/bash

# Bash script to install, run (AI chat with) and uninstall Ollama (and optionally the friendlier Open-WebUI interface) to provide a locally running AI chatbot.
# Ollama requires an installed large language model (LLM) - either a default model (Meta's 'fast' llama3.2:1b) or various other models can be selected. 
#
# Platform
# --------
# Ubuntu Linux 24.04.1 LTS
#
# Using
# -----
# chmod +x ./ollama.sh
# ./ollama.sh
#
# Development And Testing
# -----------------------
# Pilot: AI Playground (Quasimodo), https://redorangegreen.github.io/ai
# Copilot: ChatGPT 4o mini, https://chatgpt.com
# Last Code Update: Wed 29 Jan 2025, added the Deepseek-R1 1.5B model

set -e

# Clear the terminal screen
clear

# Display current date and time
echo "Current date and time: $(date +"%A, %d %B %Y %T")"

# Define model names
DEFAULT_MODEL_NAME="llama3.2:1b"
MODEL_NAMES=(
    "llama3.2:1b"
    "llama3.2"
    "gemma2:2b"
    "phi3.5"
    "deepseek-r1:1.5b"
)
MODEL_DESCRIPTIONS=(
    "Meta Llama 3.2 1B"
    "Meta Llama 3.2 3B"
    "Google gemma2 2B"
    "Microsoft phi3.5 3.8B"
    "DeepSeek-R1 1.5B"
)
MODEL_NAME="$DEFAULT_MODEL_NAME"

# Function to display the date and time header
display_header() {
    current_date=$(date "+%d %B %Y %H:%M:%S")
    echo "========================================"
    echo "  Ollama and Open-WebUI Manager"
    echo "  $current_date"
    echo "========================================"
    echo
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get user confirmation
get_confirmation() {
    local prompt="$1"
    local response
    read -p "$prompt (y/n): " response
    case "$response" in
        [yY]) return 0 ;;
        *) return 1 ;;
    esac
}

function check_ollama_installed() {
    if command -v ollama &> /dev/null; then
        return 0
    else
        return 1
    fi
}

function install_ollama() {
    if ! command -v curl &> /dev/null; then
        echo "Warning: curl is not installed. Ollama installation requires curl."
        echo "Please install curl and try again."
        return
    fi

    echo "Welcome to the Ollama installation script."
    read -p "Do you want to proceed with the installation? (y/n): " choice

    case "$choice" in 
        y|Y ) 
            echo "Proceeding with installation..."
            curl -fsSL https://ollama.com/install.sh | sh
            ;;
        n|N ) 
            echo "Installation cancelled."
            ;;
        * ) 
            echo "Invalid input."
            ;;
    esac
}

function chat_ollama() {
    local model=${1:-$DEFAULT_MODEL_NAME}
    if ! check_ollama_installed; then
        echo "Ollama is not installed."
        return
    fi

    echo "Pulling $model"
    ollama pull $model

    # Get the installation path
    local install_path
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        install_path="/usr/share/ollama/.ollama/models"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        install_path="$HOME/.ollama/models"
    elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* ]]; then
        install_path="$USERPROFILE\.ollama\models"
    else
        echo "Unsupported operating system. Cannot determine model installation path."
        return
    fi

    echo "Model installed at: $install_path"
    echo "Specific model files can be found in the 'blobs' and 'manifests' subdirectories."

    echo "Running $model"
    ollama run $model
}

function uninstall_ollama() {
    if ! check_ollama_installed; then
        echo "Ollama is not installed."
        return
    fi

    echo "This script will uninstall Ollama and remove all associated files."
    read -p "Do you want to proceed with the uninstall? (y/n): " confirm

    if [[ $confirm != [Yy]* ]]; then
        echo "Uninstall cancelled."
        return
    fi

    echo "Proceeding with Ollama uninstall..."

    if systemctl is-active --quiet ollama; then
        sudo systemctl stop ollama
    fi
    if systemctl is-enabled --quiet ollama; then
        sudo systemctl disable ollama
    fi

    ollama_path=$(which ollama)
    if [ -n "$ollama_path" ]; then
        sudo rm "$ollama_path"
    fi

    if [ -f /etc/systemd/system/ollama.service ]; then
        sudo rm /etc/systemd/system/ollama.service
    fi

    if [ -d /usr/share/ollama ]; then
        sudo rm -r /usr/share/ollama
    fi

    if id "ollama" &>/dev/null; then
        sudo userdel ollama
    fi
    if getent group ollama >/dev/null; then
        sudo groupdel ollama
    fi

    if [ -d ~/.ollama ]; then
        rm -rf ~/.ollama
    fi

    if command -v updatedb &> /dev/null; then
        sudo updatedb
    fi

    echo "Ollama uninstall completed."
}

function select_model() {
    echo "Select Ollama Model:"
    for i in "${!MODEL_NAMES[@]}"; do
        echo "$((i+1)). ${MODEL_DESCRIPTIONS[i]}"
    done
    echo "$((${#MODEL_NAMES[@]}+1)). Back to main menu"

    read -p "Enter your choice (1-$((${#MODEL_NAMES[@]}+1))): " model_choice

    if [[ "$model_choice" -ge 1 && "$model_choice" -le "${#MODEL_NAMES[@]}" ]]; then
        MODEL_NAME="${MODEL_NAMES[$((model_choice-1))]}"
        echo "Selected model: $MODEL_NAME"
    elif [[ "$model_choice" -eq $((${#MODEL_NAMES[@]}+1)) ]]; then
        return
    else
        echo "Invalid choice. Please try again."
        select_model
    fi
}

# Function to install Open-WebUI
install_open_webui() {
    echo "Preparing to install Open-WebUI..."
    if get_confirmation "Are you sure you want to install Open-WebUI?"; then
        echo "Purging pip cache..."
        pip cache purge || { echo "Error: Failed to purge pip cache"; return 1; }

        echo "Checking Python installation..."
        if ! command_exists python3; then
            echo "Error: Python 3 is not installed. Please install Python 3.11 or above and try again."
            return 1
        fi

        echo "Checking Python version..."
        python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if [ "$(printf '%s\n' "3.11" "$python_version" | sort -V | head -n1)" != "3.11" ]; then
            echo "Error: Python version 3.11 or above is required. Current version: $python_version"
            return 1
        fi

        echo "Creating virtual environment..."
        python3 -m venv open-webui-env || { echo "Error: Failed to create virtual environment"; return 1; }

        echo "Activating virtual environment..."
        source open-webui-env/bin/activate || { echo "Error: Failed to activate virtual environment"; return 1; }

        echo "Installing Open-WebUI..."
        pip install open-webui || { echo "Error: Failed to install Open WebUI"; return 1; }

        echo "Upgrading required modules..."
        pip install -U Pillow pyopenssl || { echo "Error: Failed to upgrade required modules"; return 1; }

        echo "Open-WebUI installed successfully."
    else
        echo "Installation cancelled."
    fi
}

# Function to start Open-WebUI
start_open_webui() {
    echo "Preparing to start Open-WebUI..."
    if get_confirmation "Are you sure you want to start Open-WebUI?"; then
        if [ -d "open-webui-env" ]; then
            echo "Activating virtual environment..."
            source open-webui-env/bin/activate
            echo "Starting Open-WebUI server..."
            open-webui serve || { echo "Error: Failed to start Open WebUI server"; return 1; }
        else
            echo "Error: Open-WebUI environment not found. Please install it first."
        fi
    else
        echo "Start operation cancelled."
    fi
}

# Function to uninstall Open-WebUI
uninstall_open_webui() {
    echo "Checking for Open-WebUI installation..."
    if [ -d "open-webui-env" ]; then
        if get_confirmation "Are you sure you want to uninstall Open-WebUI?"; then
            echo "Removing Open-WebUI environment..."
            rm -rf open-webui-env
            echo "Open-WebUI uninstalled successfully."
        else
            echo "Uninstallation cancelled."
        fi
    else
        echo "Open-WebUI is not installed."
    fi
}

while true; do
    clear
    display_header
    echo "Ollama and Open-WebUI Management Script"
    echo "1. Install Ollama"
    echo "2. Chat With Ollama (Using Default Model: $DEFAULT_MODEL_NAME)"
    echo "3. Chat With Ollama (Choose Model)"
    echo "4. Uninstall Ollama"
    echo "5. Install Open-WebUI"
    echo "6. Start Open-WebUI"
    echo "7. Uninstall Open-WebUI"
    echo "8. Exit"
    
    read -p "Enter your choice (1-8): " choice

    case $choice in
        1) 
            if check_ollama_installed; then
                echo "Ollama is already installed."
            else
                install_ollama
            fi
            ;;
        2) chat_ollama "$DEFAULT_MODEL_NAME" ;;
        3) 
            if check_ollama_installed; then
                select_model
                if [[ $model_choice != $((${#MODEL_NAMES[@]}+1)) ]]; then
                    chat_ollama "$MODEL_NAME"
                fi
            else
                echo "Ollama is not installed. Please install Ollama first."
            fi
            ;;
        4) uninstall_ollama ;;
        5) install_open_webui ;;
        6) start_open_webui ;;
        7) uninstall_open_webui ;;
        8) echo "Exiting..."; exit 0 ;;
        *) echo "Invalid choice. Please enter a number between 1 and 8." ;;
    esac

    echo
    read -p "Press Enter to return to the main menu..."
done
