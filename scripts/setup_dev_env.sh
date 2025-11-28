#!/usr/bin/env zsh
# Create a local virtual environment and install dev requirements
set -euo pipefail

HERE=$(cd "$(dirname "$0")/.." && pwd)
VENV="$HERE/.venv"

if [ ! -d "$VENV" ]; then
  echo "Creating virtualenv at $VENV"
  python3 -m venv "$VENV"
fi

echo "Activating virtualenv"
source "$VENV/bin/activate"

echo "Upgrading pip, setuptools, wheel"
pip install --upgrade pip setuptools wheel

echo "Installing development requirements (includes great_expectations)"
pip install -r "$HERE/requirements-dev.txt"

echo "Installing project in editable mode"
pip install -e "$HERE"

echo "Done. To activate the environment: source $VENV/bin/activate"
