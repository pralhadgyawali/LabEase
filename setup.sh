#!/bin/bash

# LabEase Setup Script
# This script sets up the LabEase Django project

set -e  # Exit on error

echo "========================================="
echo "LabEase Setup Script"
echo "========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is available
if ! python3 -m pip --version &> /dev/null; then
    echo "Installing pip..."
    python3 -m ensurepip --upgrade || {
        echo "Error: Could not install pip. Please install pip manually."
        exit 1
    }
fi

echo "✓ pip found"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv || {
        echo "Error: Could not create virtual environment."
        echo "You may need to install python3-venv: sudo apt install python3-venv"
        exit 1
    }
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
echo ""
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "Warning: requirements.txt not found. Installing basic dependencies..."
    pip install Django==5.2.8 openpyxl==3.1.5
fi

# Run migrations
echo ""
echo "Running database migrations..."
python manage.py migrate --noinput
echo "✓ Database migrations completed"

# Load sample data
echo ""
read -p "Do you want to load sample data (tests and labs)? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Loading sample data..."
    python manage.py load_sample_data
    echo "✓ Sample data loaded"
fi

# Create superuser (optional)
echo ""
read -p "Do you want to create a superuser? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

echo ""
echo "========================================="
echo "Setup completed successfully!"
echo "========================================="
echo ""
echo "To start the server, run:"
echo "  ./start.sh"
echo ""
echo "Or manually:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
