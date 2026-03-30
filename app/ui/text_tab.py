"""Text-to-speech tab"""

import uuid
from datetime import datetime

from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QSlider,
    QGroupBox,
    QFileDialog,
    QMessageBox,
    QProgressBar,
)

from ..audio.player import AudioPlayer
from ..audio.exporter import AudioExporter
from ..core.history import HistoryEntry


class _TTSWorker(QtCore.QObject):
    """Background worker for TTS synthesis."""

    finished = QtCore.Signal(bytes)
    error = QtCore.Signal(str)

    def __init__(self, api_client, text, config):
        super().__init__()
        self._api_client = api_client
        self._text = text
        self._config = config

    def run(self):
        try:
            result = self._api_client.synthesize(self._text, self._config)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class TextTab(QWidget):
    def __init__(self, api_client, history_manager):
        super().__init__()
        self.api_client = api_client
        self.history_manager = history_manager
        self.audio_player = AudioPlayer()
        self.current_audio: bytes | None = None
        self._thread: QtCore.QThread | None = None
        self._pending_text: str = ""

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        input_group = QGroupBox("文字輸入")
        input_layout = QVBoxLayout(input_group)
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("請輸入要合成的文字...")
        self.text_input.setMinimumHeight(120)
        input_layout.addWidget(self.text_input)
        layout.addWidget(input_group)

        params_group = QGroupBox("合成參數")
        params_layout = QHBoxLayout(params_group)

        speed_layout = QVBoxLayout()
        speed_layout.addWidget(QLabel("語速"))
        self.speed_slider = QSlider(QtCore.Qt.Horizontal)
        self.speed_slider.setRange(50, 200)
        self.speed_slider.setValue(100)
        self.speed_label = QLabel("1.0x")
        self.speed_slider.valueChanged.connect(
            lambda v: self.speed_label.setText(f"{v / 100:.1f}x")
        )
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_label)
        params_layout.addLayout(speed_layout)

        pitch_layout = QVBoxLayout()
        pitch_layout.addWidget(QLabel("音調"))
        self.pitch_slider = QSlider(QtCore.Qt.Horizontal)
        self.pitch_slider.setRange(50, 200)
        self.pitch_slider.setValue(100)
        self.pitch_label = QLabel("1.0x")
        self.pitch_slider.valueChanged.connect(
            lambda v: self.pitch_label.setText(f"{v / 100:.1f}x")
        )
        pitch_layout.addWidget(self.pitch_slider)
        pitch_layout.addWidget(self.pitch_label)
        params_layout.addLayout(pitch_layout)

        volume_layout = QVBoxLayout()
        volume_layout.addWidget(QLabel("音量"))
        self.volume_slider = QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_label = QLabel("1.0")
        self.volume_slider.valueChanged.connect(
            lambda v: self.volume_label.setText(f"{v / 100:.1f}")
        )
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_label)
        params_layout.addLayout(volume_layout)

        layout.addWidget(params_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        button_layout = QHBoxLayout()
        self.synthesize_btn = QPushButton("合成")
        self.synthesize_btn.clicked.connect(self._on_synthesize)
        button_layout.addWidget(self.synthesize_btn)

        self.play_btn = QPushButton("播放")
        self.play_btn.clicked.connect(self._on_play)
        self.play_btn.setEnabled(False)
        button_layout.addWidget(self.play_btn)

        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self._on_stop)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)

        self.export_btn = QPushButton("匯出")
        self.export_btn.clicked.connect(self._on_export)
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)

        layout.addLayout(button_layout)

    def _on_synthesize(self):
        text = self.text_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "警告", "請輸入要合成的文字")
            return

        if self._thread and self._thread.isRunning():
            return

        from ..api.qwen3_client import TTSConfig

        config = TTSConfig(
            speed=self.speed_slider.value() / 100,
            pitch=self.pitch_slider.value() / 100,
            volume=self.volume_slider.value() / 100,
        )

        self._pending_text = text
        self._pending_config = config
        self.synthesize_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        self._thread = QtCore.QThread()
        self._worker = _TTSWorker(self.api_client, text, config)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_synthesis_done)
        self._worker.error.connect(self._on_synthesis_error)
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.start()

    def _on_synthesis_done(self, audio_data: bytes):
        self.current_audio = audio_data

        entry = HistoryEntry(
            id=self.history_manager.generate_id(),
            timestamp=datetime.now().isoformat(),
            operation="tts",
            text=self._pending_text,
            config={
                "speed": self._pending_config.speed,
                "pitch": self._pending_config.pitch,
                "volume": self._pending_config.volume,
            },
            audio_duration=AudioExporter.get_info(audio_data)["duration"],
        )
        self.history_manager.add(entry)

        self.play_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        self.synthesize_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def _on_synthesis_error(self, error: str):
        QMessageBox.critical(self, "錯誤", f"合成失敗：{error}")
        self.synthesize_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def _on_play(self):
        if self.current_audio:
            if self.audio_player.is_playing():
                self.audio_player.pause()
                self.play_btn.setText("繼續")
            else:
                self.audio_player.play(self.current_audio)
                self.play_btn.setText("暫停")

    def _on_stop(self):
        self.audio_player.stop()
        self.play_btn.setText("播放")

    def _on_export(self):
        if not self.current_audio:
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "匯出音訊", "", "WAV 音訊 (*.wav);;所有檔案 (*.*)"
        )
        if path:
            try:
                AudioExporter.to_wav(self.current_audio, path)
                QMessageBox.information(self, "成功", f"已匯出至：{path}")
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"匯出失敗：{str(e)}")
