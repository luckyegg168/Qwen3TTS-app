#!/bin/bash

# Qwen3-TTS Desktop Application Startup Script

# Note: no 'set -e' — API checks may fail without killing the script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================"
echo " Qwen3-TTS Desktop Application"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3.8 or higher."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if config.yaml exists
if [ ! -f "config.yaml" ]; then
    echo "Creating config.yaml from example..."
    cp config.example.yaml config.yaml
    echo ""
    echo "Please edit config.yaml to configure your API endpoints."
fi

# Check Ollama connection
echo ""
echo "Checking Ollama connection..."
python3 -c "
import sys
sys.path.insert(0, '.')
from app.api.ollama_client import OllamaClient
try:
    client = OllamaClient()
    if client.health_check():
        print('Ollama: Connected')
        models = client.list_models()
        print(f'Available models: {len(models)}')
    else:
        print('Ollama: Not connected (make sure Ollama is running)')
except Exception as e:
    print(f'Ollama: Not connected ({e})')
" 2>/dev/null || echo "Ollama: Not connected"

# Check Qwen3-TTS connection
echo ""
echo "Checking Qwen3-TTS connection..."
python3 -c "
import sys
sys.path.insert(0, '.')
from app.api.qwen3_client import Qwen3Client
try:
    client = Qwen3Client()
    if client.health_check():
        print('Qwen3-TTS: Connected')
    else:
        print('Qwen3-TTS: Not connected (make sure Qwen3-TTS API is running)')
except Exception as e:
    print(f'Qwen3-TTS: Not connected ({e})')
" 2>/dev/null || echo "Qwen3-TTS: Not connected"

echo ""
echo "============================================"
echo " Starting application..."
echo "============================================"
echo ""

# Run the application
python3 -m app.main
