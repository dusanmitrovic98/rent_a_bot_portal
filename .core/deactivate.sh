#!/bin/bash
# Check if environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "No active virtual environment."
    exit 1
fi

deactivate