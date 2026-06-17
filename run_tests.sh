#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Setting up virtual environment for testing..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
echo "Installing package and development dependencies..."
pip install -e .[dev]

echo "Running tests..."
pytest tests/

echo "Tests completed successfully!"
