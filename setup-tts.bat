@echo off
REM ============================================================
REM  setup-tts.bat — Setup venv-tts and launch Qwen3-TTS server
REM ============================================================
REM
REM  Usage:
REM    setup-tts.bat                      (CPU, port 8000)
REM    setup-tts.bat --port 8001          (custom port)
REM    setup-tts.bat --device cuda        (NVIDIA GPU)
REM    setup-tts.bat --model-id Qwen/Qwen3-TTS-1.7B
REM
REM  All extra arguments are forwarded to scripts\tts_server.py.
REM ============================================================

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo ============================================
echo  Qwen3-TTS Server Setup ^& Launch
echo ============================================
echo.

REM ── Python check ──────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not on PATH.
    echo         Install Python 3.10 or higher from https://python.org
    pause
    exit /b 1
)

REM ── Create venv-tts if it does not exist ──────────────────────────────────
if not exist "venv-tts" (
    echo [INFO] Creating virtual environment venv-tts ...
    python -m venv venv-tts
    if errorlevel 1 (
        echo [ERROR] Failed to create venv-tts.
        pause
        exit /b 1
    )
    echo [INFO] venv-tts created.
) else (
    echo [INFO] venv-tts already exists, skipping creation.
)

REM ── Activate venv-tts ─────────────────────────────────────────────────────
echo [INFO] Activating venv-tts ...
call venv-tts\Scripts\activate.bat

REM ── Upgrade pip ───────────────────────────────────────────────────────────
echo [INFO] Upgrading pip ...
python -m pip install --upgrade pip --quiet

REM ── Install / update dependencies ─────────────────────────────────────────
echo [INFO] Installing requirements-tts.txt ...
pip install -r requirements-tts.txt
if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    echo         If you need CUDA support, edit requirements-tts.txt and swap
    echo         the torch lines as instructed, then re-run this script.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Starting Qwen3-TTS server ...
echo  Press Ctrl+C to stop.
echo ============================================
echo.

REM ── Launch server — all CLI arguments are passed through ──────────────────
python scripts\tts_server.py %*

echo.
echo [INFO] Server stopped.
pause
