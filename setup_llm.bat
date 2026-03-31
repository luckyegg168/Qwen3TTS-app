@echo off
REM ============================================================
REM  setup_llm.bat — 建立 venv-llm 並啟動本地 LLM 伺服器
REM
REM  用法:
REM    setup_llm.bat                           （預設 Qwen3-0.6B, port 8001）
REM    setup_llm.bat --model-id Qwen3-1.7B
REM    setup_llm.bat --device cuda
REM    setup_llm.bat --port 8002
REM
REM  所有多餘參數會傳遞給 scripts\llm_server.py
REM ============================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================
echo  Qwen3-LLM Server Setup ^& Launch
echo ============================================
echo.

REM ── Python check ──────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 未安裝或不在 PATH 中。
    pause & exit /b 1
)

REM ── Create venv-llm ───────────────────────────────────────────────────────
if not exist "venv-llm" (
    echo [INFO] 建立 venv-llm ...
    python -m venv venv-llm
    if errorlevel 1 (
        echo [ERROR] 建立虛擬環境失敗。
        pause & exit /b 1
    )
) else (
    echo [INFO] venv-llm 已存在，跳過建立。
)

REM ── Activate & upgrade pip ────────────────────────────────────────────────
call venv-llm\Scripts\activate.bat
python -m pip install --upgrade pip --quiet

REM ── Install dependencies ──────────────────────────────────────────────────
echo [INFO] 安裝 requirements-llm.txt ...
pip install -r requirements-llm.txt
if errorlevel 1 (
    echo [ERROR] 依賴安裝失敗。請檢查 requirements-llm.txt 或網路連線。
    pause & exit /b 1
)

REM ── Check model exists ────────────────────────────────────────────────────
if not exist "models\Qwen3-0.6B\config.json" (
    if not exist "models\Qwen3-1.7B\config.json" (
        if not exist "models\Qwen3-4B\config.json" (
            echo.
            echo [WARN] 尚未下載 LLM 模型。
            echo        請先執行 download_models.bat 並選擇 LLM 模型 ^(6/7/8^)
            echo        或執行: download_models.bat --group llm
            echo.
        )
    )
)

echo.
echo ============================================
echo  啟動 Qwen3-LLM 伺服器 ...
echo  預設: http://localhost:8001
echo  設定 ^> 潤稿翻譯 ^> 模式: fastapi
echo              Base URL: http://localhost:8001
echo  按 Ctrl+C 停止伺服器
echo ============================================
echo.

python scripts\llm_server.py %*

echo.
echo [INFO] 伺服器已停止。
pause
endlocal
