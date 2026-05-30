from __future__ import annotations
import time

from pathlib import Path

from PySide6.QtCore import QSettings, Qt, QThreadPool, QTimer
from PySide6.QtGui import QAction, QActionGroup, QDesktopServices, QPainter, QPen
from PySide6.QtWidgets import (
    QCheckBox,
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
    QStyle,
    QStyleOptionButton,
)
from PySide6.QtCore import QUrl

from app.core.model_manager import MODEL_DEFS, ModelManager
from app.core.notices import THIRD_PARTY_NOTICE_TEXT
from app.core.paths import outputs_dir
from app.core.transcriber import TranscriptionOptions
from app.ui.widgets import DropLabel
from app.ui.workers import DownloadModelWorker, TranscribeWorker
from app.version import APP_VERSION


THEME_PALETTES = {
    "light": {
        "app_bg": "#f4f7fb",
        "root_text": "#172635",
        "menu_bg": "#f4f7fb",
        "menu_text": "#243545",
        "menu_hover": "#e3edf5",
        "menu_panel": "#ffffff",
        "menu_border": "#d2dde7",
        "title": "#102131",
        "muted": "#647789",
        "label": "#263949",
        "status_text": "#526678",
        "status_bg": "#ffffff",
        "status_border": "#d7e1ea",
        "section_title": "#142536",
        "drop_text": "#0d5d67",
        "drop_bg": "#edf8fb",
        "drop_border": "#86b7c5",
        "drop_hover_bg": "#e1f5f6",
        "drop_hover_border": "#0aa37f",
        "group_text": "#142536",
        "group_bg": "#ffffff",
        "group_border": "#d8e2eb",
        "group_title_bg": "#f4f7fb",
        "field_label": "#627486",
        "button_text": "#203140",
        "button_bg": "#edf3f8",
        "button_border": "#cddbe5",
        "button_hover_bg": "#e3edf5",
        "button_hover_border": "#b8cbd8",
        "button_pressed_bg": "#d9e7ef",
        "button_disabled_text": "#98a7b4",
        "button_disabled_bg": "#edf1f4",
        "button_disabled_border": "#dbe3ea",
        "primary_text": "#06251e",
        "primary_bg": "#1cc79a",
        "primary_border": "#18b58c",
        "primary_hover_bg": "#27d9aa",
        "danger_text": "#fff7f8",
        "danger_bg": "#c83d55",
        "danger_border": "#b9344b",
        "danger_hover_bg": "#d84f66",
        "secondary_bg": "#f7fafc",
        "secondary_border": "#cddbe5",
        "input_text": "#142536",
        "input_bg": "#ffffff",
        "input_border": "#ccd9e4",
        "input_hover_border": "#8fb0c4",
        "input_hover_bg": "#fbfdff",
        "arrow": "#0aa37f",
        "list_text": "#263949",
        "list_bg": "#ffffff",
        "list_border": "#d7e1ea",
        "list_hover_bg": "#c8eadf",
        "list_hover_text": "#102131",
        "selection_bg": "#d9f4ec",
        "selection_text": "#102131",
        "progress_bg": "#e2eaf1",
        "progress_chunk": "#1cc79a",
        "splitter": "#d5e0e9",
        "scrollbar": "#c4d2dd",
    },
    "dark": {
        "app_bg": "#0d151f",
        "root_text": "#e8f1f8",
        "menu_bg": "#0d151f",
        "menu_text": "#d9e8f1",
        "menu_hover": "#1b2a37",
        "menu_panel": "#121d27",
        "menu_border": "#253847",
        "title": "#f6fbff",
        "muted": "#89a2b2",
        "label": "#dce9f1",
        "status_text": "#93aabb",
        "status_bg": "#111c26",
        "status_border": "#223240",
        "section_title": "#f6fbff",
        "drop_text": "#dffaf5",
        "drop_bg": "#101c27",
        "drop_border": "#3a6070",
        "drop_hover_bg": "#122535",
        "drop_hover_border": "#64f0cf",
        "group_text": "#f2f7fb",
        "group_bg": "#111c26",
        "group_border": "#223443",
        "group_title_bg": "#0d151f",
        "field_label": "#91a7b6",
        "button_text": "#e8f1f8",
        "button_bg": "#182737",
        "button_border": "#314758",
        "button_hover_bg": "#213547",
        "button_hover_border": "#45667a",
        "button_pressed_bg": "#10202d",
        "button_disabled_text": "#647987",
        "button_disabled_bg": "#111922",
        "button_disabled_border": "#1f2a34",
        "primary_text": "#05201d",
        "primary_bg": "#72f2d3",
        "primary_border": "#72f2d3",
        "primary_hover_bg": "#8dffe3",
        "danger_text": "#ffe9ec",
        "danger_bg": "#4b202a",
        "danger_border": "#6f3441",
        "danger_hover_bg": "#682938",
        "secondary_bg": "#142331",
        "secondary_border": "#2e4557",
        "input_text": "#eff8fd",
        "input_bg": "#0c1721",
        "input_border": "#2d4354",
        "input_hover_border": "#4f788d",
        "input_hover_bg": "#101f2c",
        "arrow": "#72f2d3",
        "list_text": "#dbe9f1",
        "list_bg": "#081019",
        "list_border": "#223443",
        "list_hover_bg": "#243f51",
        "list_hover_text": "#ffffff",
        "selection_bg": "#1f3d4c",
        "selection_text": "#ffffff",
        "progress_bg": "#162431",
        "progress_chunk": "#72f2d3",
        "splitter": "#182532",
        "scrollbar": "#2f4656",
    },
}


class XCheckBox(QCheckBox):
    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        if not self.isChecked():
            return

        option = QStyleOptionButton()
        self.initStyleOption(option)
        indicator = self.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, option, self)
        margin = 4

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(Qt.GlobalColor.black, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(
            indicator.left() + margin,
            indicator.top() + margin,
            indicator.right() - margin,
            indicator.bottom() - margin,
        )
        painter.drawLine(
            indicator.right() - margin,
            indicator.top() + margin,
            indicator.left() + margin,
            indicator.bottom() - margin,
        )


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
        self.auto_model_prompted = False
        self.settings = QSettings("Transcriber-LP", "Transcriber-LP")
        saved_theme = self.settings.value("appearance/theme", "light")
        self.theme_name = saved_theme if saved_theme in THEME_PALETTES else "light"
        self.log_auto_scroll = self._settings_bool("log/auto_scroll", True)

        self._build_ui()
        self.refresh_models()
        QTimer.singleShot(250, self.ensure_default_model_available)

    def _build_ui(self) -> None:
        menu_bar = self.menuBar()
        view_menu = menu_bar.addMenu("View")
        theme_menu = view_menu.addMenu("Theme")
        self.theme_actions = QActionGroup(self)
        self.theme_actions.setExclusive(True)

        self.light_theme_action = QAction("Light", self)
        self.light_theme_action.setCheckable(True)
        self.light_theme_action.triggered.connect(lambda: self.set_theme("light"))
        self.theme_actions.addAction(self.light_theme_action)
        theme_menu.addAction(self.light_theme_action)

        self.dark_theme_action = QAction("Dark", self)
        self.dark_theme_action.setCheckable(True)
        self.dark_theme_action.triggered.connect(lambda: self.set_theme("dark"))
        self.theme_actions.addAction(self.dark_theme_action)
        theme_menu.addAction(self.dark_theme_action)

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

        browse_btn = QPushButton("Browse file…")
        browse_btn.setObjectName("browseButton")
        browse_btn.setProperty("role", "secondary")
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
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
        for combo in (
            self.output_combo,
            self.model_combo,
            self.source_language_combo,
            self.target_language_combo,
        ):
            self._configure_combo(combo)

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
        log_header = QHBoxLayout()
        log_header.setContentsMargins(0, 0, 0, 0)
        log_title = QLabel("Log")
        log_title.setObjectName("sectionTitle")
        log_header.addWidget(log_title)
        log_header.addStretch()
        self.log_auto_scroll_checkbox = XCheckBox("Auto-scroll")
        self.log_auto_scroll_checkbox.setChecked(self.log_auto_scroll)
        self.log_auto_scroll_checkbox.setToolTip("Keep the log pinned to the newest line.")
        self.log_auto_scroll_checkbox.toggled.connect(self.set_log_auto_scroll)
        log_header.addWidget(self.log_auto_scroll_checkbox)
        right_layout.addLayout(log_header)
        self.log = QPlainTextEdit()
        self.log.setObjectName("logPanel")
        self.log.setReadOnly(True)
        self.log.setToolTip("Detailed log output from transcription and downloads.")
        right_layout.addWidget(self.log)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([540, 780])
        self.set_theme(self.theme_name, persist=False)

    def set_selected_file(self, path: Path) -> None:
        self.selected_file = path
        self.file_label.setText(str(path))
        self.append_log(f"Selected: {path}")

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

    def ensure_default_model_available(self, force: bool = False) -> None:
        if self.model_combo.count() > 0 or self.current_worker is not None:
            return
        if self.auto_model_prompted and not force:
            return

        self.auto_model_prompted = True
        model = self.model_manager.default_download_model()
        answer = QMessageBox.question(
            self,
            "Download transcription model",
            (
                "No transcription model is installed.\n\n"
                f"Download {model.label} ({model.size_label}) now?\n"
                "The file will be saved in your Application Support folder and verified by checksum."
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if answer == QMessageBox.Yes:
            self.download_model(model.key)

    def append_log(self, text: str) -> None:
        scroll_bar = self.log.verticalScrollBar()
        previous_scroll = scroll_bar.value()
        self.log.appendPlainText(text)
        if self.log_auto_scroll:
            scroll_bar.setValue(scroll_bar.maximum())
        else:
            scroll_bar.setValue(previous_scroll)

    def set_log_auto_scroll(self, enabled: bool) -> None:
        self.log_auto_scroll = enabled
        self.settings.setValue("log/auto_scroll", enabled)
        if enabled:
            scroll_bar = self.log.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())

    def start_transcription(self) -> None:
        if not self.selected_file:
            QMessageBox.warning(self, "Missing file", "Pick a file first.")
            return

        if self.model_combo.count() == 0:
            self.ensure_default_model_available(force=True)
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
        self.append_log("Stop requested by user...")
        worker = getattr(self, "current_worker", None)
        if worker is not None:
            try:
                worker.cancel()
            except Exception as exc:
                self.append_log(f"Stop failed: {exc}")

    def on_transcription_cancelled(self):
        self.append_log("Transcription cancelled.")
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
            "Appearance:\n"
            "- Usa View > Theme per passare tra tema chiaro e tema scuro.\n"
            "- La scelta del tema viene ricordata al prossimo avvio.\n\n"
            "Note:\n"
            "- Le trascrizioni vengono salvate in ~/Library/Application Support/Transcriber-LP/outputs.\n"
            "- I modelli scaricati vengono memorizzati in ~/Library/Application Support/Transcriber-LP/models.\n"
            "- Se non è presente nessun modello, l'app propone il download verificato del modello Base.\n"
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

    def _settings_bool(self, key: str, default: bool) -> bool:
        value = self.settings.value(key, default)
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() not in {"0", "false", "no", "off"}

    def _configure_combo(self, combo: QComboBox) -> None:
        combo.setCursor(Qt.CursorShape.PointingHandCursor)
        combo.view().setCursor(Qt.CursorShape.PointingHandCursor)
        combo.view().setMouseTracking(True)
        combo.view().setUniformItemSizes(True)

    def _set_download_controls_enabled(self, enabled: bool) -> None:
        for button in getattr(self, "download_buttons", []):
            button.setEnabled(enabled)

    def set_theme(self, theme_name: str, persist: bool = True) -> None:
        if theme_name not in THEME_PALETTES:
            theme_name = "light"

        self.theme_name = theme_name
        if persist:
            self.settings.setValue("appearance/theme", theme_name)

        self._sync_theme_actions()
        self._apply_theme()

    def _sync_theme_actions(self) -> None:
        if hasattr(self, "light_theme_action"):
            self.light_theme_action.setChecked(self.theme_name == "light")
        if hasattr(self, "dark_theme_action"):
            self.dark_theme_action.setChecked(self.theme_name == "dark")

    def _apply_theme(self) -> None:
        c = THEME_PALETTES[self.theme_name]

        def block(selector: str, body: str) -> str:
            return f"{selector} {{\n{body}\n}}\n"

        self.setStyleSheet(
            "\n".join(
                [
                    block("QMainWindow", f"background: {c['app_bg']};"),
                    block(
                        "QWidget#appRoot",
                        "\n".join(
                            [
                                f"background: {c['app_bg']};",
                                f"color: {c['root_text']};",
                                'font-family: "Inter", "SF Pro Text", "Segoe UI", sans-serif;',
                                "font-size: 13px;",
                            ]
                        ),
                    ),
                    block(
                        "QMenuBar",
                        "\n".join(
                            [
                                f"background: {c['menu_bg']};",
                                f"color: {c['menu_text']};",
                                "border: none;",
                                "padding: 4px 8px;",
                            ]
                        ),
                    ),
                    block("QMenuBar::item", "border-radius: 6px;\npadding: 6px 10px;"),
                    block("QMenuBar::item:selected", f"background: {c['menu_hover']};"),
                    block(
                        "QMenu",
                        "\n".join(
                            [
                                f"background: {c['menu_panel']};",
                                f"color: {c['root_text']};",
                                f"border: 1px solid {c['menu_border']};",
                                "border-radius: 8px;",
                                "padding: 6px;",
                            ]
                        ),
                    ),
                    block("QMenu::item", "border-radius: 6px;\npadding: 7px 24px 7px 10px;"),
                    block("QMenu::item:selected", f"background: {c['menu_hover']};"),
                    block("QLabel", f"color: {c['label']};"),
                    block(
                        "QLabel#appTitle",
                        "\n".join(
                            [
                                f"color: {c['title']};",
                                "font-size: 24px;",
                                "font-weight: 700;",
                                "letter-spacing: 0;",
                            ]
                        ),
                    ),
                    block("QLabel#appSubtitle", f"color: {c['muted']};\nfont-size: 13px;"),
                    block(
                        "QLabel#fileLabel,\nQLabel#progressLabel",
                        "\n".join(
                            [
                                f"color: {c['status_text']};",
                                f"background: {c['status_bg']};",
                                f"border: 1px solid {c['status_border']};",
                                "border-radius: 8px;",
                                "padding: 7px 10px;",
                            ]
                        ),
                    ),
                    block(
                        "QLabel#sectionTitle",
                        f"color: {c['section_title']};\nfont-size: 15px;\nfont-weight: 700;",
                    ),
                    block(
                        "QLabel#dropZone",
                        "\n".join(
                            [
                                f"color: {c['drop_text']};",
                                f"background: {c['drop_bg']};",
                                f"border: 2px dashed {c['drop_border']};",
                                "border-radius: 14px;",
                                "padding: 18px;",
                                "font-size: 18px;",
                                "font-weight: 700;",
                            ]
                        ),
                    ),
                    block(
                        "QLabel#dropZone:hover",
                        "\n".join(
                            [
                                f"background: {c['drop_hover_bg']};",
                                f"border-color: {c['drop_hover_border']};",
                                f"color: {c['title']};",
                            ]
                        ),
                    ),
                    block(
                        "QGroupBox",
                        "\n".join(
                            [
                                f"color: {c['group_text']};",
                                f"background: {c['group_bg']};",
                                f"border: 1px solid {c['group_border']};",
                                "border-radius: 10px;",
                                "margin-top: 10px;",
                                "font-size: 14px;",
                                "font-weight: 700;",
                            ]
                        ),
                    ),
                    block(
                        "QGroupBox::title",
                        "\n".join(
                            [
                                "subcontrol-origin: margin;",
                                "subcontrol-position: top left;",
                                "left: 14px;",
                                "padding: 0 8px;",
                                f"color: {c['group_text']};",
                                f"background: {c['group_title_bg']};",
                            ]
                        ),
                    ),
                    block("QFormLayout QLabel", f"color: {c['field_label']};\nfont-weight: 600;"),
                    block(
                        "QPushButton",
                        "\n".join(
                            [
                                "min-height: 28px;",
                                f"border: 1px solid {c['button_border']};",
                                "border-radius: 8px;",
                                "padding: 5px 12px;",
                                f"color: {c['button_text']};",
                                f"background: {c['button_bg']};",
                                "font-weight: 650;",
                            ]
                        ),
                    ),
                    block(
                        "QPushButton:hover",
                        f"background: {c['button_hover_bg']};\nborder-color: {c['button_hover_border']};",
                    ),
                    block("QPushButton:pressed", f"background: {c['button_pressed_bg']};"),
                    block(
                        "QPushButton:disabled",
                        "\n".join(
                            [
                                f"color: {c['button_disabled_text']};",
                                f"background: {c['button_disabled_bg']};",
                                f"border-color: {c['button_disabled_border']};",
                            ]
                        ),
                    ),
                    block(
                        'QPushButton[role="primary"]',
                        "\n".join(
                            [
                                f"color: {c['primary_text']};",
                                f"background: {c['primary_bg']};",
                                f"border-color: {c['primary_border']};",
                            ]
                        ),
                    ),
                    block(
                        'QPushButton[role="primary"]:hover',
                        f"background: {c['primary_hover_bg']};\nborder-color: {c['primary_hover_bg']};",
                    ),
                    block(
                        'QPushButton[role="danger"]',
                        "\n".join(
                            [
                                f"color: {c['danger_text']};",
                                f"background: {c['danger_bg']};",
                                f"border-color: {c['danger_border']};",
                            ]
                        ),
                    ),
                    block(
                        'QPushButton[role="danger"]:hover',
                        f"background: {c['danger_hover_bg']};\nborder-color: {c['danger_hover_bg']};",
                    ),
                    block(
                        'QPushButton[role="secondary"]',
                        f"background: {c['secondary_bg']};\nborder-color: {c['secondary_border']};",
                    ),
                    block(
                        "QPushButton#browseButton",
                        "\n".join(
                            [
                                "min-height: 32px;",
                                f"color: {c['title']};",
                                f"background: {c['input_bg']};",
                                f"border: 2px solid {c['primary_border']};",
                                "font-weight: 700;",
                            ]
                        ),
                    ),
                    block(
                        "QPushButton#browseButton:hover",
                        "\n".join(
                            [
                                f"background: {c['primary_bg']};",
                                f"border-color: {c['primary_hover_bg']};",
                                f"color: {c['primary_text']};",
                            ]
                        ),
                    ),
                    block("QPushButton#browseButton:pressed", f"background: {c['primary_hover_bg']};"),
                    block(
                        "QComboBox",
                        "\n".join(
                            [
                                "min-height: 28px;",
                                f"color: {c['input_text']};",
                                f"background: {c['input_bg']};",
                                f"border: 1px solid {c['input_border']};",
                                "border-radius: 8px;",
                                "padding: 4px 30px 4px 10px;",
                            ]
                        ),
                    ),
                    block(
                        "QComboBox:hover",
                        f"border-color: {c['input_hover_border']};\nbackground: {c['input_hover_bg']};",
                    ),
                    block(
                        "QComboBox:focus",
                        f"border-color: {c['primary_border']};\nbackground: {c['input_hover_bg']};",
                    ),
                    block("QComboBox::drop-down", "width: 28px;\nborder: none;"),
                    block(
                        "QComboBox::down-arrow",
                        "\n".join(
                            [
                                "image: none;",
                                "width: 0;",
                                "height: 0;",
                                "border-left: 5px solid transparent;",
                                "border-right: 5px solid transparent;",
                                f"border-top: 6px solid {c['arrow']};",
                                "margin-right: 10px;",
                            ]
                        ),
                    ),
                    block(
                        "QComboBox QAbstractItemView",
                        "\n".join(
                            [
                                f"color: {c['input_text']};",
                                f"background: {c['group_bg']};",
                                f"selection-background-color: {c['selection_bg']};",
                                f"selection-color: {c['selection_text']};",
                                f"border: 1px solid {c['input_border']};",
                                "outline: 0;",
                            ]
                        ),
                    ),
                    block(
                        "QComboBox QAbstractItemView::item",
                        "min-height: 26px;\npadding: 5px 10px;",
                    ),
                    block(
                        "QComboBox QAbstractItemView::item:hover",
                        f"background: {c['list_hover_bg']};\ncolor: {c['list_hover_text']};",
                    ),
                    block(
                        "QComboBox QAbstractItemView::item:selected",
                        f"background: {c['selection_bg']};\ncolor: {c['selection_text']};",
                    ),
                    block(
                        "QCheckBox",
                        "\n".join(
                            [
                                f"color: {c['field_label']};",
                                "font-weight: 600;",
                                "spacing: 7px;",
                            ]
                        ),
                    ),
                    block(
                        "QCheckBox::indicator",
                        "\n".join(
                            [
                                "width: 14px;",
                                "height: 14px;",
                                f"border: 1px solid {c['input_border']};",
                                "border-radius: 4px;",
                                f"background: {c['input_bg']};",
                            ]
                        ),
                    ),
                    block(
                        "QCheckBox::indicator:checked",
                        "\n".join(
                            [
                                f"background: {c['primary_bg']};",
                                f"border-color: {c['primary_border']};",
                            ]
                        ),
                    ),
                    block(
                        "QListWidget,\nQPlainTextEdit",
                        "\n".join(
                            [
                                f"color: {c['list_text']};",
                                f"background: {c['list_bg']};",
                                f"border: 1px solid {c['list_border']};",
                                "border-radius: 10px;",
                                "padding: 8px;",
                                f"selection-background-color: {c['selection_bg']};",
                                f"selection-color: {c['selection_text']};",
                            ]
                        ),
                    ),
                    block(
                        "QPlainTextEdit#logPanel",
                        'font-family: "Menlo", "Consolas", monospace;\nfont-size: 12px;\nline-height: 1.4;',
                    ),
                    block("QListWidget::item", "border-radius: 7px;\npadding: 5px 7px;\nmargin: 2px;"),
                    block("QListWidget::item:selected", f"background: {c['selection_bg']};"),
                    block(
                        "QProgressBar",
                        "\n".join(
                            [
                                "height: 8px;",
                                "border: none;",
                                "border-radius: 4px;",
                                f"background: {c['progress_bg']};",
                                "color: transparent;",
                            ]
                        ),
                    ),
                    block(
                        "QProgressBar::chunk",
                        f"border-radius: 4px;\nbackground: {c['progress_chunk']};",
                    ),
                    block(
                        "QSplitter::handle",
                        f"background: {c['splitter']};\nmargin: 4px 0;\nborder-radius: 2px;",
                    ),
                    block("QSplitter::handle:horizontal", "width: 4px;"),
                    block("QScrollBar:vertical", "background: transparent;\nwidth: 10px;\nmargin: 2px;"),
                    block(
                        "QScrollBar::handle:vertical",
                        f"background: {c['scrollbar']};\nborder-radius: 5px;\nmin-height: 28px;",
                    ),
                    block("QScrollBar::add-line:vertical,\nQScrollBar::sub-line:vertical", "height: 0;"),
                ]
            )
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
