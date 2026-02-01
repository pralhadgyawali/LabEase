#!/bin/bash

# LabEase Start Script
# This script starts the Django development server

set -e  # Exit on error

echo "========================================="
echo "Starting LabEase"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found."
    echo "Please run ./setup.sh first to set up the project."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if migrations are up to date
echo ""
echo "Checking database migrations..."
python manage.py migrate --noinput

# Collect static files (if needed in production)
# python manage.py collectstatic --noinput

# Start the server
echo ""
echo "Starting Django development server..."
echo "Server will be available at: http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""
echo "========================================="
echo ""

python manage.py runserver
