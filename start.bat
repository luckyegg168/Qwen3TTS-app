@echo off
REM Qwen3-TTS Desktop Application Startup Script

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo ============================================
echo  Qwen3-TTS Desktop Application
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed.
    echo Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Check if config.yaml exists
if not exist "config.yaml" (
    echo Creating config.yaml from example...
    copy config.example.yaml config.yaml
    echo.
    echo Please edit config.yaml to configure your API endpoints.
)

REM Check Ollama connection
echo.
echo Checking Ollama connection...
python -c "import sys; sys.path.insert(0,'.');from app.api.ollama_client import OllamaClient; client = OllamaClient(); print('Ollama: Connected' if client.health_check() else 'Ollama: Not connected')" 2>nul || echo Ollama: Not connected

REM Check Qwen3-TTS connection
echo.
echo Checking Qwen3-TTS connection...
python -c "import sys; sys.path.insert(0,'.');from app.api.qwen3_client import Qwen3Client; client = Qwen3Client(); print('Qwen3-TTS: Connected' if client.health_check() else 'Qwen3-TTS: Not connected')" 2>nul || echo Qwen3-TTS: Not connected

echo.
echo ============================================
echo  Starting application...
echo ============================================
echo.

REM Run the application
python -m app.main

if errorlevel 1 (
    echo.
    echo Application exited with error code: %errorlevel%
    pause
)

endlocal
