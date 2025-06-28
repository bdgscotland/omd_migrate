#!/bin/bash
# OpenMetadata Migration Tool Setup Script
# Sets up virtual environment and installs dependencies

set -e  # Exit on any error

VENV_NAME="omd_venv"
PYTHON_VERSION="python3"

echo "🚀 Setting up OpenMetadata Migration Tool"
echo "=========================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Get Python version
PYTHON_VER=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "✅ Found Python $PYTHON_VER"

# Check minimum Python version (3.8+)
PYTHON_MAJOR=$(echo $PYTHON_VER | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VER | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "❌ Error: Python 3.8+ is required, found $PYTHON_VER"
    exit 1
fi

# Remove existing virtual environment if it exists
if [ -d "$VENV_NAME" ]; then
    echo "🗑️  Removing existing virtual environment..."
    rm -rf "$VENV_NAME"
fi

# Create virtual environment
echo "📦 Creating virtual environment '$VENV_NAME'..."
python3 -m venv "$VENV_NAME"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "$VENV_NAME/bin/activate"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "📋 Installing production dependencies..."
    pip install -r requirements.txt
else
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

# Install development dependencies if available
if [ -f "requirements-dev.txt" ]; then
    echo "🔧 Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

# Create .env file from template if it doesn't exist
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your OpenMetadata credentials"
fi

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Activate the virtual environment: source $VENV_NAME/bin/activate"
echo "2. Edit .env file with your OpenMetadata server details"
echo "3. Test the connection: python export.py --dry-run"
echo ""
echo "📖 Quick commands:"
echo "   Export data:  python export.py"
echo "   Import data:  python import.py"
echo "   Run tests:    pytest test_migration.py -v"
echo "   Help:         python export.py --help"
echo ""
echo "🔗 Use 'deactivate' to exit the virtual environment when done"