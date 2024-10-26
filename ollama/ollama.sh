#!/bin/bash

# Bash script to install, run (AI chat with) and uninstall Ollama.
# Either a default LLM can be used (Meta's 'fast' llama3.2:1b) or other models selected.
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
# Copilot: Perplexity AI Free, https://www.perplexity.ai

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
)
MODEL_DESCRIPTIONS=(
    "Meta Llama 3.2 1B"
    "Meta Llama 3.2 3B"
    "Google gemma2 2B"
    "Microsoft phi3.5 3.8B"
)
MODEL_NAME="$DEFAULT_MODEL_NAME"

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

while true; do
    echo "Ollama Management Script"
    echo "1. Install Ollama"
    echo "2. Chat With Ollama (Using Default Model: $DEFAULT_MODEL_NAME)"
    echo "3. Chat With Ollama (Choose Model)"
    echo "4. Uninstall Ollama"
    echo "5. Exit"
    
    read -p "Enter your choice (1-5): " choice

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
        5) echo "Exiting..."; exit 0 ;;
        *) echo "Invalid choice. Please enter a number between 1 and 5." ;;
    esac

    echo
done
