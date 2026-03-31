@echo off
REM ============================================================
REM  download_models.bat — 下載 Qwen3 模型到 models/ 目錄
REM
REM  用法:
REM    download_models.bat                  互動式選單
REM    download_models.bat --all            下載全部模型
REM    download_models.bat --group asr      只下載 ASR 模型 (1-3)
REM    download_models.bat --group tts      只下載 TTS 模型 (4-5)
REM    download_models.bat --group llm      只下載 LLM 模型 (6-8)
REM    download_models.bat --ids 1,3,6      下載指定編號
REM
REM  模型編號：
REM    1. Qwen3-ASR-0.6B           語音辨識（快速）
REM    2. Qwen3-ASR-1.7B           語音辨識（精確）
REM    3. Qwen3-ForcedAligner-0.6B 時間軸對齊
REM    4. Qwen3-TTS-0.6B           語音合成
REM    5. Qwen3-TTS-1.7B           語音合成（高品質）
REM    6. Qwen3-0.6B               LLM 潤稿翻譯（超小）
REM    7. Qwen3-1.7B               LLM 潤稿翻譯（小型）
REM    8. Qwen3-4B                 LLM 潤稿翻譯（中型）
REM
REM  所有模型下載至 <專案根目錄>\models\
REM ============================================================

setlocal
cd /d "%~dp0"

REM ── 優先 venv-llm（專為 LLM，有 huggingface_hub）──────────────────────────
if exist "venv-llm\Scripts\python.exe" (
    echo [INFO] 使用 venv-llm 執行下載...
    venv-llm\Scripts\python.exe scripts\download_models.py %*
    goto :end
)

REM ── 次選 venv-asr ───────────────────────────────────────────────────────────
if exist "venv-asr\Scripts\python.exe" (
    echo [INFO] 使用 venv-asr 執行下載...
    venv-asr\Scripts\python.exe scripts\download_models.py %*
    goto :end
)

REM ── 次選 venv ───────────────────────────────────────────────────────────────
if exist "venv\Scripts\python.exe" (
    echo [INFO] 使用 venv 執行下載...
    venv\Scripts\python.exe -m pip install --quiet huggingface_hub tqdm
    venv\Scripts\python.exe scripts\download_models.py %*
    goto :end
)

REM ── Fallback: 系統 Python ───────────────────────────────────────────────────
echo [INFO] 使用系統 Python 執行下載...
python -m pip install --quiet huggingface_hub tqdm
python scripts\download_models.py %*

:end
echo.
pause
endlocal
