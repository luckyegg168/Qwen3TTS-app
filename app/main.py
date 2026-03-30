"""Qwen3-TTS Desktop Application - Entry Point"""

import sys
from pathlib import Path

# Ensure project root is in sys.path so 'app' package is discoverable
# when the script is run directly (python app/main.py)
_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from PySide6.QtWidgets import QApplication

from app.core.config import Config
from app.api.qwen3_client import Qwen3Client
from app.api.ollama_client import OllamaClient
from app.core.history import HistoryManager
from app.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Qwen3-TTS")
    app.setOrganizationName("Qwen3TTS")

    config_path = Path(__file__).parent.parent / "config.yaml"
    if config_path.exists():
        config = Config.from_yaml(config_path)
    else:
        config = Config()

    qwen3_client = Qwen3Client(
        base_url=config.api.qwen3_base_url,
        timeout=config.api.qwen3_timeout,
    )

    ollama_client = OllamaClient(
        base_url=config.ollama.base_url,
    )
    ollama_client.default_model = config.ollama.default_model

    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    history_path = data_dir / "history.yaml"

    history_manager = HistoryManager(
        storage_path=history_path,
        max_entries=config.history.max_entries,
    )

    window = MainWindow(
        config=config,
        qwen3_client=qwen3_client,
        ollama_client=ollama_client,
        history_manager=history_manager,
    )
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
