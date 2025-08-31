#!/bin/bash
# Startup script for Plant Disease Detection API Server on PC/Cloud

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}🌱 Plant Disease Detection API Server - Startup Script${NC}"
echo "=============================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 is not installed or not in PATH${NC}"
    echo "Please install Python3 first"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        exit 1
    fi
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Install/update requirements
echo -e "${BLUE}📦 Installing/updating requirements...${NC}"
pip install -r requirements.txt

# Create uploads directory
echo -e "${BLUE}📁 Creating uploads directory...${NC}"
mkdir -p uploads

# Check if model file exists
if [ ! -f "model/plant_disease_model.h5" ]; then
    echo -e "${YELLOW}⚠️  ML model file not found. System will use mock predictions.${NC}"
    echo -e "${YELLOW}To use real ML model, place your model file at: model/plant_disease_model.h5${NC}"
    echo -e "${YELLOW}Supported formats: .h5 (TensorFlow), .onnx, .tflite${NC}"
fi

# Test server startup
echo -e "${BLUE}🧪 Testing server startup...${NC}"
python3 -c "
from app import app
print('✅ Flask app imported successfully')
print(f'✅ App name: {app.name}')
print(f'✅ Config: {dict(app.config)}')
"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Server test failed${NC}"
    exit 1
fi

# Show server info
echo -e "${GREEN}✅ Server ready to start!${NC}"
echo -e "${BLUE}Server will be available at: http://0.0.0.0:5000${NC}"
echo -e "${BLUE}Health check: http://0.0.0.0:5000/health${NC}"
echo -e "${BLUE}Prediction endpoint: http://0.0.0.0:5000/predict${NC}"
echo "=============================================================="

# Start the server
echo -e "${GREEN}🚀 Starting Plant Disease Detection API Server...${NC}"
echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
echo "=============================================================="

# Run the Flask app
python3 app.py

# Cleanup on exit
echo -e "${BLUE}🛑 Cleaning up...${NC}"
deactivate
echo -e "${GREEN}✅ Server stopped. Goodbye!${NC}" 