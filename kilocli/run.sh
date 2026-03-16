#!/usr/bin/env bash
set -euo pipefail
source ~/.profile
if ! command -v kilo &> /dev/null; then
  echo "Kilocode CLI not found. Please run ./setup.sh first."
  exit 1
fi
kilo "$@"

