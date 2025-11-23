#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Install pip-tools if not already installed
pip install pip-tools

# Remove old requirements files to avoid conflicts
rm -f requirements.txt requirements-dev.txt

# Compile requirements.txt from pyproject.toml
pip-compile --output-file requirements.txt pyproject.toml

# Compile requirements-dev.txt with dev extras
pip-compile --extra dev --output-file requirements-dev.txt pyproject.toml

echo "Requirements files compiled successfully."
