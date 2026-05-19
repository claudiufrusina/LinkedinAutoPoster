#!/bin/bash
export PYTHONIOENCODING=utf-8

# Get the directory of the script itself
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if the virtual environment exists, otherwise use system python
if [ -f "venv/bin/python" ]; then
    ./venv/bin/python main.py
else
    python3 main.py
fi
