#!/bin/bash
# PC Master Controller Startup Script

echo "🌱 Starting Plant Disease Detection & Sprinkler Control - PC Master Controller"
echo "=================================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.12+"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create temp directory
mkdir -p temp

echo "🚀 Starting PC Master Controller..."
echo "📡 Web UI will be available at: http://localhost:5000"
echo "🔗 Pi API URL: http://192.168.1.100:5001/sprinkle"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================================="

# Start the server
python simple_app.py
