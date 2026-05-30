from __future__ import annotations
import time

from pathlib import Path

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QProgressBar,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QUrl

from app.core.model_manager import MODEL_DEFS, ModelManager
from app.core.notices import THIRD_PARTY_NOTICE_TEXT
from app.core.paths import outputs_dir
from app.core.transcriber import TranscriptionOptions
from app.ui.widgets import DropLabel
from app.ui.workers import DownloadModelWorker, TranscribeWorker
from app.version import APP_VERSION


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"Transcriber-LP {APP_VERSION}")
        self.resize(1320, 640)
        self.thread_pool = QThreadPool.globalInstance()
        self.model_manager = ModelManager()
        self.selected_file: Path | None = None
        self.current_worker = None
        self.download_started_at = 0.0
        self.active_download_model_key: str | None = None

        self._build_ui()
        self.refresh_models()

    def _build_ui(self) -> None:
        menu_bar = self.menuBar()
        help_menu = menu_bar.addMenu("Help")
        help_action = QAction("Show manual", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        licenses_action = QAction("Open-source licenses", self)
        licenses_action.triggered.connect(self.show_open_source_notices)
        help_menu.addAction(licenses_action)
        about_action = QAction("About Transcriber-LP", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        central = QWidget()
        central.setObjectName("appRoot")
        root = QVBoxLayout(central)
        root.setContentsMargins(22, 16, 22, 16)
        root.setSpacing(10)

        header = QWidget()
        header.setObjectName("header")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)

        title = QLabel("Transcriber-LP")
        title.setObjectName("appTitle")
        subtitle = QLabel("Offline media transcription for clean text and subtitles")
        subtitle.setObjectName("appSubtitle")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        root.addWidget(header)

        splitter = QSplitter()
        splitter.setObjectName("mainSplitter")
        root.addWidget(splitter)
        self.setCentralWidget(central)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 14, 0)
        left_layout.setSpacing(9)

        self.drop_zone = DropLabel(self.set_selected_file)
        self.drop_zone.setToolTip("Drag and drop a media file here, or click Browse to select one.")
        left_layout.addWidget(self.drop_zone)

        browse_btn = QPushButton("Browse…")
        browse_btn.setProperty("role", "secondary")
        browse_btn.clicked.connect(self.browse_file)
        browse_btn.setToolTip("Open a file selector to choose the audio or video file to transcribe.")
        left_layout.addWidget(browse_btn)

        self.file_label = QLabel("No file selected")
        self.file_label.setObjectName("fileLabel")
        self.file_label.setWordWrap(True)
        left_layout.addWidget(self.file_label)

        settings_box = QGroupBox("Transcription")
        settings_layout = QFormLayout(settings_box)
        settings_layout.setContentsMargins(16, 20, 16, 14)
        settings_layout.setHorizontalSpacing(14)
        settings_layout.setVerticalSpacing(8)
        settings_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.output_combo = QComboBox()
        self.output_combo.addItems(["txt", "srt", "vtt"])
        self.output_combo.setToolTip("Choose the output subtitle/text format for the transcription.")
        settings_layout.addRow("Output format", self.output_combo)

        self.model_combo = QComboBox()
        self.model_combo.setToolTip("Select the transcription model. Models are loaded from the app bundle or downloaded models.")
        self.source_language_combo = QComboBox()
        self.source_language_combo.addItem("Auto-detect", "auto")
        self.source_language_combo.addItem("Italian", "it")
        self.source_language_combo.addItem("English", "en")
        self.source_language_combo.addItem("Spanish", "es")
        self.source_language_combo.addItem("Portuguese", "pt")
        self.source_language_combo.addItem("French", "fr")
        self.source_language_combo.addItem("German", "de")
        self.source_language_combo.setToolTip("Force the source language for transcription, or use auto-detection.")
        self.target_language_combo = QComboBox()
        self.target_language_combo.addItem("Keep original language", "as_source")
        self.target_language_combo.addItem("Translate to English", "english")
        self.target_language_combo.setToolTip("Choose whether to keep the original language or translate the transcript into English.")

        settings_layout.addRow("Model", self.model_combo)
        settings_layout.addRow("Source language", self.source_language_combo)
        settings_layout.addRow("Translation target", self.target_language_combo)

        left_layout.addWidget(settings_box)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        self.transcribe_btn = QPushButton("Transcribe")
        self.transcribe_btn.setProperty("role", "primary")
        self.transcribe_btn.clicked.connect(self.start_transcription)
        self.transcribe_btn.setToolTip("Start the transcription process for the selected file.")
        button_row.addWidget(self.transcribe_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setProperty("role", "danger")
        self.stop_btn.clicked.connect(self.stop_transcription)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setToolTip("Cancel the currently running transcription.")
        button_row.addWidget(self.stop_btn)

        self.open_output_btn = QPushButton("Open outputs")
        self.open_output_btn.setProperty("role", "secondary")
        self.open_output_btn.clicked.connect(self.open_outputs)
        self.open_output_btn.setToolTip("Open the folder where transcription outputs are saved.")
        button_row.addWidget(self.open_output_btn)
        left_layout.addLayout(button_row)

        model_box = QGroupBox("Model Manager")
        model_layout = QVBoxLayout(model_box)
        model_layout.setContentsMargins(16, 20, 16, 14)
        model_layout.setSpacing(8)
        self.model_list = QListWidget()
        self.model_list.setMinimumHeight(76)
        self.model_list.setMaximumHeight(94)
        self.model_list.setToolTip("Installed and bundled models available for transcription.")
        model_layout.addWidget(self.model_list)

        dl_row = QHBoxLayout()
        dl_row.setSpacing(8)
        self.download_base_btn = QPushButton("Download Base")
        self.download_base_btn.setProperty("role", "secondary")
        self.download_base_btn.clicked.connect(lambda: self.download_model("base"))
        self.download_base_btn.setToolTip("Download the small base model for faster transcription.")
        dl_row.addWidget(self.download_base_btn)

        self.download_small_btn = QPushButton("Download Small")
        self.download_small_btn.setProperty("role", "secondary")
        self.download_small_btn.clicked.connect(lambda: self.download_model("small"))
        self.download_small_btn.setToolTip("Download the small multilingual model.")
        dl_row.addWidget(self.download_small_btn)

        self.download_medium_btn = QPushButton("Download Medium")
        self.download_medium_btn.setProperty("role", "secondary")
        self.download_medium_btn.clicked.connect(lambda: self.download_model("medium"))
        self.download_medium_btn.setToolTip("Download the medium multilingual model.")
        dl_row.addWidget(self.download_medium_btn)

        self.download_large_btn = QPushButton("Download Large Turbo")
        self.download_large_btn.setProperty("role", "secondary")
        self.download_large_btn.clicked.connect(lambda: self.download_model("large-v3-turbo-q5_0"))
        self.download_large_btn.setToolTip("Download the large turbo quantized model.")
        dl_row.addWidget(self.download_large_btn)
        self.download_buttons = [
            self.download_base_btn,
            self.download_small_btn,
            self.download_medium_btn,
            self.download_large_btn,
        ]

        model_layout.addLayout(dl_row)
        left_layout.addWidget(model_box)

        self.progress = QProgressBar()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setToolTip("Shows the current progress of downloads or transcription.")
        left_layout.addWidget(self.progress)

        self.progress_label = QLabel("Ready")
        self.progress_label.setObjectName("progressLabel")
        self.progress_label.setWordWrap(True)
        self.progress_label.setToolTip("Current status of the application.")
        left_layout.addWidget(self.progress_label)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(14, 0, 0, 0)
        right_layout.setSpacing(8)
        log_title = QLabel("Log")
        log_title.setObjectName("sectionTitle")
        right_layout.addWidget(log_title)
        self.log = QPlainTextEdit()
        self.log.setObjectName("logPanel")
        self.log.setReadOnly(True)
        self.log.setToolTip("Detailed log output from transcription and downloads.")
        right_layout.addWidget(self.log)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([540, 780])
        self._apply_theme()

    def set_selected_file(self, path: Path) -> None:
        self.selected_file = path
        self.file_label.setText(str(path))
        self.log.appendPlainText(f"Selected: {path}")

    def browse_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Pick media file",
            str(Path.home()),
            "Media files (*.mp4 *.mov *.mkv *.avi *.mp3 *.wav *.m4a *.aac *.flac);;All files (*.*)",
        )
        if file_path:
            self.set_selected_file(Path(file_path))

    def refresh_models(self) -> None:
        self.model_combo.clear()
        self.model_list.clear()
        items = self.model_manager.available_models()
        medium_index = -1
        for idx, (key, path, source) in enumerate(items):
            display = MODEL_DEFS.get(key).label if key in MODEL_DEFS else key
            self.model_combo.addItem(f"{display} ({source})", userData=key)
            self.model_list.addItem(QListWidgetItem(f"{display} — {source} — {path.name}"))
            if key == "medium":
                medium_index = idx

        if medium_index >= 0:
            self.model_combo.setCurrentIndex(medium_index)

        if not items:
            self.model_list.addItem("No model found")

    def append_log(self, text: str) -> None:
        self.log.appendPlainText(text)

    def start_transcription(self) -> None:
        if not self.selected_file:
            QMessageBox.warning(self, "Missing file", "Pick a file first.")
            return

        if self.model_combo.count() == 0:
            QMessageBox.warning(self, "Missing model", "No model available.")
            return

        model_key = self.model_combo.currentData()
        try:
            model_file = self.model_manager.resolve_model_path(model_key)
        except Exception as exc:
            QMessageBox.critical(self, "Model error", str(exc))
            return

        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Select output folder",
            str(Path.home())
        )
        if not output_dir:
            return

        self.transcribe_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self._set_download_controls_enabled(False)
        self.progress_label.setText("Preparing transcription...")

        opts = TranscriptionOptions(
            input_file=self.selected_file,
            model_file=model_file,
            language=self.source_language_combo.currentData() or "auto",
            output_format=self.output_combo.currentText(),
            target_language=self.target_language_combo.currentData() or "as_source",
            output_dir=output_dir,
        )
        self.progress.setRange(0, 0)
        self.append_log("Starting transcription...")
        worker = TranscribeWorker(opts)
        worker.signals.log.connect(self.append_log)
        worker.signals.error.connect(self.on_worker_error)
        worker.signals.finished.connect(self.on_transcription_finished)
        worker.signals.cancelled.connect(self.on_transcription_cancelled)
        self.current_worker = worker
        self.thread_pool.start(worker)

    def on_transcription_finished(self, output_path) -> None:
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.progress.setFormat("Done")
        self.progress_label.setText("Transcription complete")
        self.append_log(f"Done: {output_path}")
        QMessageBox.information(self, "Completed", f"Output saved to:\n{output_path}")
        self.transcribe_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self._set_download_controls_enabled(True)
        self.current_worker = None

    def on_worker_error(self, message: str) -> None:
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress.setFormat("%p%")
        self.progress_label.setText("Stopped")
        self.append_log(f"ERROR: {message}")
        QMessageBox.critical(self, "Error", message)
        self._set_download_controls_enabled(True)
        self.transcribe_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.current_worker = None

    def open_outputs(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(outputs_dir())))

    def download_model(self, model_key: str) -> None:
        model = MODEL_DEFS.get(model_key)
        label = model.label if model else model_key
        self.append_log(f"Downloading model: {label}")
        self.progress_label.setText(f"Preparing download: {label}")
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFormat("%p%")
        self.download_started_at = time.monotonic()
        self.active_download_model_key = model_key
        self._set_download_controls_enabled(False)
        self.transcribe_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        worker = DownloadModelWorker(model_key, self.model_manager)
        worker.signals.progress.connect(self.on_download_progress)
        worker.signals.error.connect(self.on_worker_error)
        worker.signals.finished.connect(self.on_download_finished)
        self.current_worker = worker
        self.thread_pool.start(worker)

    def on_download_progress(self, done: int, total: int) -> None:
        label = self.active_download_model_key or "model"
        if label in MODEL_DEFS:
            label = MODEL_DEFS[label].label
        elapsed = max(time.monotonic() - self.download_started_at, 0.001)
        speed = done / elapsed

        if total <= 0:
            self.progress.setRange(0, 0)
            self.progress_label.setText(
                f"Downloading {label}: {_format_bytes(done)} downloaded at {_format_bytes(speed)}/s"
            )
            return

        percent = max(0, min(100, int(done * 100 / total)))
        self.progress.setRange(0, 100)
        self.progress.setValue(percent)
        self.progress.setFormat(f"{percent}%")
        self.progress_label.setText(
            f"Downloading {label}: {_format_bytes(done)} / {_format_bytes(total)} at {_format_bytes(speed)}/s"
        )

    def on_download_finished(self, path) -> None:
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.progress.setFormat("Done")
        self.progress_label.setText(f"Download complete: {Path(path).name}")
        self.append_log(f"Model downloaded: {path}")
        self.refresh_models()
        self._set_download_controls_enabled(True)
        self.transcribe_btn.setEnabled(True)
        self.current_worker = None
        self.active_download_model_key = None



    def stop_transcription(self):
        self.log.appendPlainText("Stop requested by user...")
        worker = getattr(self, "current_worker", None)
        if worker is not None:
            try:
                worker.cancel()
            except Exception as exc:
                self.log.appendPlainText(f"Stop failed: {exc}")

    def on_transcription_cancelled(self):
        self.log.appendPlainText("Transcription cancelled.")
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress_label.setText("Cancelled")
        self.transcribe_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self._set_download_controls_enabled(True)
        self.current_worker = None

    def show_help(self) -> None:
        manual = (
            "Transcriber-LP Manual:\n\n"
            "1) Seleziona un file audio o video con Browse o trascinalo nella finestra.\n"
            "2) Scegli il formato di uscita: txt, srt o vtt.\n"
            "3) Seleziona un modello disponibile. I modelli possono essere aggiornati dal pannello Model Manager.\n"
            "4) Opzionalmente imposta la lingua sorgente o lascia Auto-detect per la rilevazione automatica.\n"
            "5) Scegli se mantenere la lingua originale o tradurre in inglese.\n"
            "6) Clicca Transcribe per avviare; usa Stop per annullare la trascrizione in corso.\n\n"
            "Note:\n"
            "- Le trascrizioni vengono salvate in ~/Library/Application Support/Transcriber-LP/outputs.\n"
            "- I modelli scaricati vengono memorizzati in ~/Library/Application Support/Transcriber-LP/models.\n"
            "- Assicurati di avere i binari ffmpeg e whisper-cli in third_party/macos quando crei il bundle.\n"
            "- Usa solo componenti open source e conserva le attribuzioni in docs/THIRD_PARTY_NOTICE.md.\n"
        )
        QMessageBox.information(self, "User Manual", manual)

    def show_open_source_notices(self) -> None:
        QMessageBox.information(self, "Open-source licenses", THIRD_PARTY_NOTICE_TEXT)

    def show_about(self) -> None:
        QMessageBox.information(
            self,
            "About Transcriber-LP",
            (
                f"Transcriber-LP {APP_VERSION}\n\n"
                "Offline desktop transcription app for macOS.\n"
                "Versioning starts at 0.1.0 for the first tracked public-ready baseline."
            ),
        )

    def _set_download_controls_enabled(self, enabled: bool) -> None:
        for button in getattr(self, "download_buttons", []):
            button.setEnabled(enabled)

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow {
                background: #0d151f;
            }

            QWidget#appRoot {
                background: #0d151f;
                color: #e8f1f8;
                font-family: "Inter", "SF Pro Text", "Segoe UI", sans-serif;
                font-size: 13px;
            }

            QMenuBar {
                background: #0d151f;
                color: #d9e8f1;
                border: none;
                padding: 4px 8px;
            }

            QMenuBar::item {
                border-radius: 6px;
                padding: 6px 10px;
            }

            QMenuBar::item:selected {
                background: #1b2a37;
            }

            QMenu {
                background: #121d27;
                color: #e8f1f8;
                border: 1px solid #253847;
                border-radius: 8px;
                padding: 6px;
            }

            QMenu::item {
                border-radius: 6px;
                padding: 7px 24px 7px 10px;
            }

            QMenu::item:selected {
                background: #213545;
            }

            QLabel {
                color: #dce9f1;
            }

            QLabel#appTitle {
                color: #f6fbff;
                font-size: 24px;
                font-weight: 700;
                letter-spacing: 0;
            }

            QLabel#appSubtitle {
                color: #89a2b2;
                font-size: 13px;
            }

            QLabel#fileLabel,
            QLabel#progressLabel {
                color: #93aabb;
                background: #111c26;
                border: 1px solid #223240;
                border-radius: 8px;
                padding: 7px 10px;
            }

            QLabel#sectionTitle {
                color: #f6fbff;
                font-size: 15px;
                font-weight: 700;
            }

            QLabel#dropZone {
                color: #dffaf5;
                background: #101c27;
                border: 2px dashed #3a6070;
                border-radius: 14px;
                padding: 18px;
                font-size: 18px;
                font-weight: 700;
            }

            QLabel#dropZone:hover {
                background: #122535;
                border-color: #64f0cf;
                color: #ffffff;
            }

            QGroupBox {
                color: #f2f7fb;
                background: #111c26;
                border: 1px solid #223443;
                border-radius: 10px;
                margin-top: 10px;
                font-size: 14px;
                font-weight: 700;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 14px;
                padding: 0 8px;
                color: #f2f7fb;
                background: #0d151f;
            }

            QFormLayout QLabel {
                color: #91a7b6;
                font-weight: 600;
            }

            QPushButton {
                min-height: 28px;
                border: 1px solid #314758;
                border-radius: 8px;
                padding: 5px 12px;
                color: #e8f1f8;
                background: #182737;
                font-weight: 650;
            }

            QPushButton:hover {
                background: #213547;
                border-color: #45667a;
            }

            QPushButton:pressed {
                background: #10202d;
            }

            QPushButton:disabled {
                color: #647987;
                background: #111922;
                border-color: #1f2a34;
            }

            QPushButton[role="primary"] {
                color: #05201d;
                background: #72f2d3;
                border-color: #72f2d3;
            }

            QPushButton[role="primary"]:hover {
                background: #8dffe3;
                border-color: #8dffe3;
            }

            QPushButton[role="danger"] {
                color: #ffe9ec;
                background: #4b202a;
                border-color: #6f3441;
            }

            QPushButton[role="danger"]:hover {
                background: #682938;
                border-color: #965164;
            }

            QPushButton[role="secondary"] {
                background: #142331;
                border-color: #2e4557;
            }

            QComboBox {
                min-height: 28px;
                color: #eff8fd;
                background: #0c1721;
                border: 1px solid #2d4354;
                border-radius: 8px;
                padding: 4px 30px 4px 10px;
            }

            QComboBox:hover {
                border-color: #4f788d;
                background: #101f2c;
            }

            QComboBox::drop-down {
                width: 28px;
                border: none;
            }

            QComboBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #72f2d3;
                margin-right: 10px;
            }

            QComboBox QAbstractItemView {
                color: #eff8fd;
                background: #111c26;
                selection-background-color: #1f3d4c;
                border: 1px solid #2d4354;
                outline: 0;
            }

            QListWidget,
            QPlainTextEdit {
                color: #dbe9f1;
                background: #081019;
                border: 1px solid #223443;
                border-radius: 10px;
                padding: 8px;
                selection-background-color: #1f3d4c;
                selection-color: #ffffff;
            }

            QPlainTextEdit#logPanel {
                font-family: "Menlo", "Consolas", monospace;
                font-size: 12px;
                line-height: 1.4;
            }

            QListWidget::item {
                border-radius: 7px;
                padding: 5px 7px;
                margin: 2px;
            }

            QListWidget::item:selected {
                background: #1f3d4c;
            }

            QProgressBar {
                height: 8px;
                border: none;
                border-radius: 4px;
                background: #162431;
                color: transparent;
            }

            QProgressBar::chunk {
                border-radius: 4px;
                background: #72f2d3;
            }

            QSplitter::handle {
                background: #182532;
                margin: 4px 0;
                border-radius: 2px;
            }

            QSplitter::handle:horizontal {
                width: 4px;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 2px;
            }

            QScrollBar::handle:vertical {
                background: #2f4656;
                border-radius: 5px;
                min-height: 28px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
            """
        )


def _format_bytes(value):
    size = float(value or 0)
    units = ["B", "KiB", "MiB", "GiB"]
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
