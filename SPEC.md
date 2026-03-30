# Qwen3-TTS 桌面應用程式規格書

## 1. 專案概述

**專案名稱：** Qwen3-TTS Desktop  
**專案類型：** 桌面應用程式（PySide6）  
**核心功能：** 
- 文字轉語音合成
- 語音克隆（文字參考 + 音檔參考）
- 潤稿翻譯（本地 Ollama 模型）
- 簡繁轉換
- 歷史記錄管理

---

## 2. 技術架構

### 2.1 系統架構圖

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            GUI Layer (PySide6)                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                         QTabWidget                                  │ │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────────┐      │ │
│  │  │ 文字合成分頁 │ │ 語音克隆分頁 │ │ 潤稿翻譯分頁 │ │   設定分頁    │      │ │
│  │  │  TextTab  │ │  CloneTab │ │ EditTab   │ │ SettingsTab  │      │ │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────────┘      │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Service Layer                                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐          │
│  │  AudioPlayer    │ │  AudioExporter  │ │ HistoryManager  │          │
│  │  (QtMultimedia) │ │   (soundfile)  │ │    (YAML)      │          │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘          │
│  ┌─────────────────┐ ┌─────────────────┐                               │
│  │ OllamaClient    │ │ ChineseConverter│                               │
│  │  (requests)    │ │   (opencc)     │                               │
│  └─────────────────┘ └─────────────────┘                               │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Backend Services                              │
│  ┌───────────────────────┐     ┌───────────────────────┐               │
│  │   Qwen3-TTS API       │     │    Ollama API         │               │
│  │  (文字合成/語音克隆)     │     │  (潤稿/翻譯模型)       │               │
│  │ localhost:8000         │     │ localhost:11434        │               │
│  └───────────────────────┘     └───────────────────────┘               │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 模組依賴關係

```
main.py
    └── MainWindow
            ├── TextTab
            │       ├── AudioPlayer
            │       ├── AudioExporter
            │       ├── Qwen3Client
            │       └── HistoryManager
            ├── CloneTab
            │       ├── AudioPlayer
            │       ├── AudioExporter
            │       ├── Qwen3Client
            │       └── HistoryManager
            ├── EditTab (NEW)
            │       ├── OllamaClient (NEW)
            │       ├── ChineseConverter (NEW)
            │       ├── Qwen3Client
            │       └── HistoryManager
            └── SettingsTab
                    ├── Config
                    └── OllamaConfig (NEW)
```

---

## 3. 功能規格

### 3.1 文字合成（Text-to-Speech）

| 功能 | 說明 |
|------|------|
| 文字輸入 | 多行文字輸入框 |
| 語速調整 | 0.5x ~ 2.0x，預設 1.0x |
| 音調調整 | 0.5x ~ 2.0x，預設 1.0x |
| 音量調整 | 0.0 ~ 1.0，預設 1.0 |
| 播放控制 | 播放/暫停/停止 |
| 音訊匯出 | 支援 WAV 格式 |
| 快速潤稿 | 一鍵將輸入文字送往潤稿翻譯分頁 |

### 3.2 語音克隆（Voice Clone）

| 功能 | 說明 |
|------|------|
| 模式一：文字參考 | 輸入參考文字，使用相同音色朗讀目標文字 |
| 模式二：音檔參考 | 上傳參考音檔（.wav/.mp3），克隆該音色 |
| 語速調整 | 0.5x ~ 2.0x，預設 1.0x |
| 音量調整 | 0.0 ~ 1.0，預設 1.0 |
| 播放控制 | 播放/暫停/停止 |
| 音訊匯出 | 支援 WAV 格式 |

### 3.3 潤稿翻譯（Edit & Translate）★★★ NEW

| 功能 | 說明 |
|------|------|
| 原文輸入 | 多行文字輸入框 |
| 潤稿處理 | 使用 Ollama 模型優化文字（修正語法、順暢語句） |
| 翻譯處理 | 使用 Ollama 模型翻譯（支援多語言） |
| 語言方向 | 原文語言 → 目標語言 |
| 快速轉換 | 潤稿/翻譯結果一鍵送往文字合成 |
| 簡繁轉換 | 潤稿/翻譯結果可切换簡體/繁體 ★★ NEW |

**支援的處理模式：**
- 潤稿（保持原語言）
- 中文簡→繁
- 中文繁→簡
- 英→中翻譯
- 中→英翻譯
- 日→中翻譯
- 自訂指令（Prompt）

### 3.4 簡繁轉換（Chinese Converter）★★★ NEW

| 功能 | 說明 |
|------|------|
| 簡→繁 | 簡體中文轉繁體中文 |
| 繁→簡 | 繁體中文轉簡體中文 |
| 批量轉換 | 支援大段文字 |
| 詞彙對照 | 支援地區用詞差異（台/港/陸） |

### 3.5 歷史記錄（History）★★★ NEW

| 功能 | 說明 |
|------|------|
| 瀏覽記錄 | 清單檢視所有歷史項目 |
| 操作類型 | 區分 TTS/Clone/Edit 類型 |
| 詳情檢視 | 檢視歷史項目的完整內容 |
| 重新執行 | 從歷史記錄快速重複操作 |
| 刪除記錄 | 支援刪除單筆或清空全部 |
| 匯出文字 | 將歷史文字內容複製到剪貼簿 |

---

## 4. API 介面規格

### 4.1 Qwen3-TTS API

#### 文字合成
```
POST /tts
{
  "text": "要合成的文字",
  "speed": 1.0,
  "pitch": 1.0,
  "volume": 1.0,
  "format": "wav"
}
→ Binary audio (audio/wav)
```

#### 語音克隆（文字參考）
```
POST /clone/text
{
  "text": "要合成的文字",
  "ref_text": "參考文字",
  ...
}
→ Binary audio (audio/wav)
```

#### 語音克隆（音檔參考）
```
POST /clone/audio
{
  "text": "要合成的文字",
  "ref_audio": "<base64>",
  ...
}
→ Binary audio (audio/wav)
```

### 4.2 Ollama API

#### 文字生成
```
POST /api/generate
{
  "model": "llama3.2:latest",
  "prompt": "prompt text",
  "stream": false
}
→ {"response": "..."}
```

---

## 5. 專案結構（更新）

```
Qwen3TTS-app/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── text_tab.py
│   │   ├── clone_tab.py
│   │   ├── edit_tab.py          ★ NEW
│   │   ├── history_tab.py        ★ NEW
│   │   └── settings_tab.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── qwen3_client.py
│   │   ├── ollama_client.py      ★ NEW
│   │   └── exceptions.py
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── player.py
│   │   └── exporter.py
│   └── core/
│       ├── __init__.py
│       ├── config.py
│       ├── history.py
│       └── chinese_converter.py  ★ NEW
├── requirements.txt
├── config.example.yaml
├── SPEC.md
└── README.md
```

---

## 6. 依賴套件（更新）

| 套件 | 版本 | 用途 |
|------|------|------|
| PySide6 | >=6.6.0 | GUI 框架 |
| pydantic | >=2.0.0 | 資料驗證 |
| PyYAML | >=6.0 | 設定檔讀寫 |
| requests | >=2.31.0 | HTTP 客戶端 |
| soundfile | >=0.12.0 | 音訊檔案處理 |
| numpy | >=1.24.0 | 音訊資料處理 |
| opencc-python | >=0.1.0 | 簡繁轉換 ★ NEW |

---

## 7. 實作進度

| 階段 | 狀態 | 說明 |
|------|------|------|
| 1. 專案結構建立 | ✅ | 目錄、__init__.py |
| 2. Core 模組 | ✅ | Config, HistoryManager |
| 3. API 客戶端 | ✅ | Qwen3Client |
| 4. Audio 模組 | ✅ | AudioPlayer, AudioExporter |
| 5. UI 層 | ⏳ | MainWindow, Tabs |
| 6. Ollama 客戶端 | ⏳ | NEW - 待實作 |
| 7. 簡繁轉換 | ⏳ | NEW - 待實作 |
| 8. 潤稿翻譯分頁 | ⏳ | NEW - 待實作 |
| 9. 歷史記錄分頁 | ⏳ | NEW - 待實作 |
| 10. README | ⏳ | 待建立 |

---

## 8. 待實作項目

### 8.1 OllamaClient (`app/api/ollama_client.py`)
```python
class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434")
    def generate(self, prompt: str, model: str) -> str
    def polish(self, text: str, model: str) -> str
    def translate(self, text: str, from_lang: str, to_lang: str, model: str) -> str
    def health_check(self) -> bool
```

### 8.2 ChineseConverter (`app/core/chinese_converter.py`)
```python
class ChineseConverter:
    def __init__(self, mode: str = "t2s")  # t2s=繁→簡, s2t=簡→繁
    def convert(self, text: str) -> str
    @staticmethod
    def s2t(text: str) -> str: ...  # 簡→繁
    @staticmethod
    def t2s(text: str) -> str: ...  # 繁→簡
```

### 8.3 EditTab (`app/ui/edit_tab.py`)
- 原文輸入框
- 模式選擇（潤稿/翻譯/簡繁）
- 目標語言選擇
- 處理按鈕
- 結果輸出框
- 發送至合成按鈕

### 8.4 HistoryTab (`app/ui/history_tab.py`)
- 歷史記錄列表（QListWidget）
- 篩選功能（依類型）
- 詳情面板
- 操作按鈕（重新執行/刪除/複製）
