#!/bin/bash
set -e

# Publishing script for Flask-MonitoringDashboard
# Usage: ./publish.sh
# Reads PYPI_TOKEN from .env file or environment variable

# Load .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

if [ -z "$PYPI_TOKEN" ]; then
    echo "Error: PYPI_TOKEN environment variable is not set"
    echo "Create a .env file with: PYPI_TOKEN=your-token"
    echo "Or use: PYPI_TOKEN=your-token ./publish.sh"
    exit 1
fi

# Get version from constants.json
VERSION=$(python3 -c "import json; print(json.load(open('flask_monitoringdashboard/constants.json'))['version'])")
echo "Publishing Flask-MonitoringDashboard version $VERSION"

# Confirm
read -p "Are you sure you want to publish version $VERSION to PyPI? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Clean old builds
echo "Cleaning old builds..."
rm -rf dist build *.egg-info

# Determine which Python to use (prefer venv if available)
if [ -d ".venv/bin" ]; then
    PYTHON=".venv/bin/python3"
elif [ -d "venv/bin" ]; then
    PYTHON="venv/bin/python3"
else
    PYTHON="python3"
fi

echo "Using Python: $PYTHON"

# Build
echo "Building distribution packages..."
$PYTHON -m build

# Upload to PyPI
echo "Uploading to PyPI..."
TWINE_USERNAME=__token__ TWINE_PASSWORD=$PYPI_TOKEN $PYTHON -m twine upload dist/*

echo "Successfully published version $VERSION!"
echo "View at: https://pypi.org/project/Flask-MonitoringDashboard/$VERSION/"
