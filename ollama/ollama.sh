#!/bin/bash

# Bash script to install, run (Using Meta's llama3.2:1b) and uninstall Ollama
# Free, fast, anonymous AI chat running on your computer has now arrived!
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
# Pilot: AI Playground (Quasimodo) https://redorangegreen.github.io/ai
# Copilot: Perplexity AI Free https://www.perplexity.ai

function check_ollama_installed() {
    if command -v ollama &> /dev/null; then
        return 0
    else
        return 1
    fi
}

function install_ollama() {
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
    MODEL_NAME="llama3.2:1b"

    if ! check_ollama_installed; then
        echo "Ollama is not installed."
        return
    fi

    echo "Pulling $MODEL_NAME"
    ollama pull $MODEL_NAME

    echo "Running $MODEL_NAME"
    ollama run $MODEL_NAME
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

while true; do
    echo "Ollama Management Script"
    echo "1. Install Ollama"
    echo "2. Chat with Ollama"
    echo "3. Uninstall Ollama"
    echo "4. Exit"
    read -p "Enter your choice (1-4): " choice

    case $choice in
        1) 
            if check_ollama_installed; then
                echo "Ollama is already installed."
            else
                install_ollama
            fi
            ;;
        2) chat_ollama ;;
        3) uninstall_ollama ;;
        4) echo "Exiting..."; exit 0 ;;
        *) echo "Invalid choice. Please enter a number between 1 and 4." ;;
    esac

    echo
done
