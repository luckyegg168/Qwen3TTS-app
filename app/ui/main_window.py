"""Main application window"""

from PySide6 import QtWidgets
from PySide6.QtWidgets import QTabWidget, QMessageBox, QLabel, QStatusBar

from .text_tab import TextTab
from .clone_tab import CloneTab
from .edit_tab import EditTab
from .history_tab import HistoryTab
from .settings_tab import SettingsTab


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, config, qwen3_client, ollama_client, history_manager):
        super().__init__()
        self.config = config
        self.qwen3_client = qwen3_client
        self.ollama_client = ollama_client
        self.history_manager = history_manager

        self._setup_ui()
        self._setup_status_bar()
        self._connect_signals()

    def _setup_ui(self):
        self.setWindowTitle("Qwen3-TTS 語音合成")
        self.resize(*self.config.ui.window_size)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        layout = QtWidgets.QVBoxLayout(central_widget)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        self.text_tab = TextTab(self.qwen3_client, self.history_manager)
        self.clone_tab = CloneTab(self.qwen3_client, self.history_manager)
        self.edit_tab = EditTab(
            self.ollama_client, self.qwen3_client, self.history_manager
        )
        self.history_tab = HistoryTab(
            self.history_manager, self.text_tab, self.clone_tab
        )
        self.settings_tab = SettingsTab(self.config)

        tabs.addTab(self.text_tab, "文字合成")
        tabs.addTab(self.clone_tab, "語音克隆")
        tabs.addTab(self.edit_tab, "潤稿翻譯")
        tabs.addTab(self.history_tab, "歷史記錄")
        tabs.addTab(self.settings_tab, "設定")

        self.tabs = tabs

    def _setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("就緒")
        self.status_bar.addPermanentWidget(self.status_label)

    def _connect_signals(self):
        self.edit_tab.text_sent.connect(self._on_text_sent_to_tts)
        self.edit_tab.text_sent_to_clone.connect(self._on_text_sent_to_clone)

    def _on_text_sent_to_tts(self, text: str):
        self.text_tab.text_input.setPlainText(text)
        self.tabs.setCurrentIndex(0)

    def _on_text_sent_to_clone(self, text: str):
        self.clone_tab.text_input.setPlainText(text)
        self.tabs.setCurrentIndex(1)

    def set_status(self, message: str):
        self.status_label.setText(message)

    def show_error(self, title: str, message: str):
        QMessageBox.critical(self, title, message)

    def show_info(self, title: str, message: str):
        QMessageBox.information(self, title, message)
