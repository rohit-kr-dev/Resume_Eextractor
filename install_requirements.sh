#!/bin/bash

echo "========================================"
echo "Creating Python virtual environment..."
echo "========================================"
python3 -m venv venv

echo "========================================"
echo "Activating virtual environment..."
echo "========================================"
source venv/bin/activate

echo "========================================"
echo "Installing required libraries from requirements.txt..."
echo "========================================"
pip install --upgrade pip
pip install -r requirements.txt

echo "========================================"
echo "✅ Setup complete! You can now run your Flask app."
echo "========================================"
