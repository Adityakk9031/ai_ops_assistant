#!/bin/bash

# AI Operations Assistant - Local Startup Script

echo "=== AI Operations Assistant Startup ==="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [ -f "venv/Scripts/activate" ]; then
    # Windows
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    # Linux/Mac
    source venv/bin/activate
else
    echo "Error: Could not find virtual environment activation script"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "WARNING: .env file not found!"
    echo "Please create .env file from .env.example and add your API keys:"
    echo "  cp .env.example .env"
    echo "  # Then edit .env with your API keys"
    echo ""
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
fi

# Get port from environment or use default
PORT=${PORT:-8000}

echo ""
echo "Starting AI Operations Assistant on port $PORT..."
echo "API will be available at: http://localhost:$PORT"
echo "API docs available at: http://localhost:$PORT/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
uvicorn main:app --reload --port $PORT
