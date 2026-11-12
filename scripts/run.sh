#!/bin/bash

set -e

cd "$(dirname "$0")/.."

echo "Food Traceability Project"
echo "------------------------"

if [ -f ".venv/Scripts/python.exe" ]; then
    PYTHON=".venv/Scripts/python.exe"
elif [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
else
    echo "Python virtual environment not found."
    echo "Create the .venv folder and install requirements.txt first."
    exit 1
fi

echo
echo "Checking the Ganache connection..."
"$PYTHON" scripts/connect.py

echo
echo "Running the food traceability demonstration..."
"$PYTHON" scripts/interact.py

echo
echo "All steps completed successfully."