#!/usr/bin/env bash
set -euo pipefail
sudo apt update
sudo apt install -y npm
npm config set prefix "$HOME/.npm-global"
if ! grep -q 'export PATH="$HOME/.npm-global/bin:$PATH"' ~/.profile; then
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
fi
export PATH="$HOME/.npm-global/bin:$PATH"
npm install -g @kilocode/cli
