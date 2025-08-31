#!/bin/bash
# Raspberry Pi Slave Controller Startup Script

echo "🌱 Starting Plant Disease Detection & Sprinkler Control - Pi Slave Controller"
echo "=================================================================="

# Check if running on Raspberry Pi
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3"
    exit 1
fi

# Check if RPi.GPIO is available
python3 -c "import RPi.GPIO" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ RPi.GPIO not found. This script must run on a Raspberry Pi"
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

echo "🚀 Starting Pi Slave Controller..."
echo "📡 API will be available at: http://0.0.0.0:5001"
echo "💧 Sprinkler GPIO Pin: 17"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================================="

# Start the server
python pi_slave_controller.py
