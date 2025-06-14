#!/bin/bash
VENV_PATH="../.venv"

# Check if .venv exists, create if missing
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_PATH" || exit 1
fi

# Source activation script
source "$VENV_PATH/bin/activate"