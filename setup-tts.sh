#!/bin/bash
# ============================================================
#  setup-tts.sh — Setup venv-tts and launch Qwen3-TTS server
# ============================================================
#
#  Usage:
#    ./setup-tts.sh                       (CPU, port 8000)
#    ./setup-tts.sh --port 8001           (custom port)
#    ./setup-tts.sh --device cuda         (NVIDIA GPU)
#    ./setup-tts.sh --model-id Qwen/Qwen3-TTS-1.7B
#
#  All extra arguments are forwarded to scripts/tts_server.py.
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================"
echo " Qwen3-TTS Server Setup & Launch"
echo "============================================"
echo ""

# ── Python check ──────────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] python3 is not installed or not on PATH."
    echo "        Install Python 3.10+ from https://python.org"
    exit 1
fi

# ── Create venv-tts if it does not exist ─────────────────────────────────────
if [ ! -d "venv-tts" ]; then
    echo "[INFO] Creating virtual environment venv-tts ..."
    python3 -m venv venv-tts
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create venv-tts."
        exit 1
    fi
    echo "[INFO] venv-tts created."
else
    echo "[INFO] venv-tts already exists, skipping creation."
fi

# ── Activate venv-tts ─────────────────────────────────────────────────────────
echo "[INFO] Activating venv-tts ..."
source venv-tts/bin/activate

# ── Upgrade pip ───────────────────────────────────────────────────────────────
echo "[INFO] Upgrading pip ..."
python -m pip install --upgrade pip --quiet

# ── Install / update dependencies ────────────────────────────────────────────
echo "[INFO] Installing requirements-tts.txt ..."
pip install -r requirements-tts.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Dependency installation failed."
    echo "        If you need CUDA support, edit requirements-tts.txt and swap"
    echo "        the torch lines as instructed, then re-run this script."
    exit 1
fi

echo ""
echo "============================================"
echo " Starting Qwen3-TTS server ..."
echo " Press Ctrl+C to stop."
echo "============================================"
echo ""

# ── Launch server — all CLI arguments are passed through ─────────────────────
python scripts/tts_server.py "$@"

echo ""
echo "[INFO] Server stopped."
