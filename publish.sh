#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Running tests before publishing..."
./run_tests.sh

echo "Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
echo "Installing build tools..."
pip install -e .[dev]

echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

echo "Building the package..."
python3 -m build

echo "Publishing to PyPI..."
python3 -m twine upload dist/*

echo "Publish complete!"
