# Qwen3-TTS Desktop

桌面版語音合成應用程式，基於 [Qwen3-TTS](https://github.com/QwenLM/Qwen3) 模型，提供文字轉語音、語音克隆、潤稿翻譯等功能。

## 功能

| 分頁 | 功能 |
|------|------|
| 文字合成 | 文字 → 語音，可調整語速 / 音調 / 音量，支援匯出 WAV |
| 語音克隆 | 以文字或音檔參考克隆音色後合成 |
| 潤稿翻譯 | 使用本地 Ollama 模型潤稿、翻譯、繁簡轉換 |
| 歷史記錄 | 瀏覽、重跑、刪除歷史合成記錄 |
| 設定 | 設定 API URL / Ollama 模型 / 視窗大小 |

## 系統需求

- Python 3.10+
- [Qwen3-TTS API server](https://github.com/QwenLM/Qwen3) 執行於 `localhost:8000`
- [Ollama](https://ollama.ai)（選用，潤稿翻譯功能）

## 快速開始

### Windows

```bat
start.bat
```

### macOS / Linux

```bash
chmod +x start.sh
./start.sh
```

### 手動安裝

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

複製設定檔並依需求修改：

```bash
cp config.example.yaml config.yaml
```

啟動應用程式：

```bash
python -m app.main
```

## 設定

編輯 `config.yaml`（預設由 `config.example.yaml` 複製）：

```yaml
api:
  qwen3_base_url: "http://localhost:8000"  # Qwen3-TTS API 位址
  qwen3_timeout: 60

ollama:
  base_url: "http://localhost:11434"
  default_model: "llama3.2:latest"        # 潤稿翻譯使用的模型

audio:
  sample_rate: 22050
  format: "wav"

ui:
  window_size: [1200, 800]

history:
  max_entries: 100
```

## 依賴套件

| 套件 | 用途 |
|------|------|
| PySide6 | GUI 框架 |
| requests | HTTP API 呼叫 |
| soundfile | WAV 音訊讀寫 |
| PyYAML | 設定檔 / 歷史記錄 |
| opencc | 繁簡中文轉換 |
| pydantic | 資料驗證 |

> **MP3 匯出（選用）**：需額外安裝 `pydub` 與 [ffmpeg](https://ffmpeg.org)。

## 授權

MIT License
