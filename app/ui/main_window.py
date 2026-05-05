from __future__ import annotations
from PySide6 import QtWidgets

from pathlib import Path

from PySide6.QtCore import Qt, QThreadPool, QTimer, QPoint
from PySide6.QtGui import QAction, QDesktopServices, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QApplication,
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
from app.core.paths import outputs_dir
from app.core.transcriber import TranscriptionOptions
from app.ui.workers import DownloadModelWorker, TranscribeWorker


class DropLabel(QLabel):
    def __init__(self, on_file_picked) -> None:
        super().__init__("Drop video/audio here or click Browse")
        self.on_file_picked = on_file_picked
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.setMinimumHeight(120)
        self.setStyleSheet(
            "border: 2px dashed #888; border-radius: 12px; padding: 16px; font-size: 16px;"
        )

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:
            path = Path(urls[0].toLocalFile())
            self.on_file_picked(path)
            event.acceptProposedAction()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Transcriber-LP")
        self.resize(1080, 720)
        self.thread_pool = QThreadPool.globalInstance()
        self.model_manager = ModelManager()
        self.selected_file: Path | None = None

        self._build_ui()
        self.refresh_models()

    def _build_ui(self) -> None:
        central = QWidget()
        root = QHBoxLayout(central)
        splitter = QSplitter()
        root.addWidget(splitter)
        self.setCentralWidget(central)
        QTimer.singleShot(0, lambda: _dedupe_source_language_controls(self))

        left = QWidget()
        left_layout = QVBoxLayout(left)

        self.drop_zone = DropLabel(self.set_selected_file)
        left_layout.addWidget(self.drop_zone)

        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self.browse_file)
        left_layout.addWidget(browse_btn)

        self.file_label = QLabel("No file selected")
        self.file_label.setWordWrap(True)
        left_layout.addWidget(self.file_label)

        settings_box = QGroupBox("Transcription")
        settings_layout = QFormLayout(settings_box)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["auto", "it", "en", "es", "pt", "de", "fr"])
        settings_layout.addRow("Source language", self.language_combo)

        self.output_combo = QComboBox()
        self.output_combo.addItems(["txt", "srt", "vtt"])
        settings_layout.addRow("Output format", self.output_combo)

        self.model_combo = QComboBox()
        self.source_language_combo = QComboBox()
        self.source_language_combo.addItem("Auto (same as source)", "auto")
        self.source_language_combo.addItem("Italian", "it")
        self.source_language_combo.addItem("English", "en")
        self.source_language_combo.addItem("Spanish", "es")
        self.source_language_combo.addItem("Portuguese", "pt")
        self.source_language_combo.addItem("French", "fr")
        self.source_language_combo.addItem("German", "de")
        self.target_language_combo = QComboBox()
        self.target_language_combo.addItem("As source", "as_source")
        self.target_language_combo.addItem("English", "english")

        settings_layout.addRow("Model", self.model_combo)
        settings_layout.addRow("Source language", self.source_language_combo)
        settings_layout.addRow("Target transcribed language", self.target_language_combo)

        left_layout.addWidget(settings_box)

        button_row = QHBoxLayout()
        self.transcribe_btn = QPushButton("Transcribe")
        self.transcribe_btn.clicked.connect(self.start_transcription)
        button_row.addWidget(self.transcribe_btn)

        self.open_output_btn = QPushButton("Open outputs")
        self.open_output_btn.clicked.connect(self.open_outputs)
        button_row.addWidget(self.open_output_btn)
        left_layout.addLayout(button_row)

        model_box = QGroupBox("Model Manager")
        model_layout = QVBoxLayout(model_box)
        self.model_list = QListWidget()
        model_layout.addWidget(self.model_list)

        dl_row = QHBoxLayout()
        self.download_base_btn = QPushButton("Download Base")
        self.download_base_btn.clicked.connect(lambda: self.download_model("base"))
        dl_row.addWidget(self.download_base_btn)

        self.download_small_btn = QPushButton("Download Small")
        self.download_small_btn.clicked.connect(lambda: self.download_model("small"))
        dl_row.addWidget(self.download_small_btn)

        self.download_medium_btn = QPushButton("Download Medium")
        self.download_medium_btn.clicked.connect(lambda: self.download_model("medium"))
        dl_row.addWidget(self.download_medium_btn)

        self.download_large_btn = QPushButton("Download Large Turbo")
        self.download_large_btn.clicked.connect(lambda: self.download_model("large-v3-turbo-q5_0"))
        dl_row.addWidget(self.download_large_btn)

        model_layout.addLayout(dl_row)
        left_layout.addWidget(model_box)

        self.progress = QProgressBar()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        left_layout.addWidget(self.progress)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(QLabel("Log"))
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        right_layout.addWidget(self.log)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([420, 660])

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

        opts = TranscriptionOptions(
            language=_resolve_source_language_from_ui(self),
            input_file=self.selected_file,
            model_file=model_file,
            output_format=self.output_combo.currentText(),
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
        self.append_log(f"Done: {output_path}")
        QMessageBox.information(self, "Completed", f"Output saved to:\n{output_path}")

    def on_worker_error(self, message: str) -> None:
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.append_log(f"ERROR: {message}")
        QMessageBox.critical(self, "Error", message)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.current_worker = None

    def open_outputs(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(outputs_dir())))

    def download_model(self, model_key: str) -> None:
        self.append_log(f"Downloading model: {model_key}")
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        worker = DownloadModelWorker(model_key)
        worker.signals.progress.connect(self.on_download_progress)
        worker.signals.error.connect(self.on_worker_error)
        worker.signals.finished.connect(self.on_download_finished)
        self.current_worker = worker
        self.thread_pool.start(worker)

    def on_download_progress(self, done: int, total: int) -> None:
        if total <= 0:
            self.progress.setRange(0, 0)
            return
        self.progress.setRange(0, 100)
        self.progress.setValue(int(done * 100 / total))

    def on_download_finished(self, path) -> None:
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.append_log(f"Model downloaded: {path}")
        self.refresh_models()



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
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.current_worker = None


def _dedupe_source_language_controls(window):
    try:
        labels = [w for w in window.findChildren(QLabel) if w.text().strip() == "Source language" and w.isVisible()]
        if len(labels) < 2:
            return
        target = labels[0]
        lp = target.mapTo(window, QPoint(0, 0))
        ly = lp.y()

        best_cb = None
        best_score = None
        for cb in window.findChildren(QComboBox):
            if not cb.isVisible():
                continue
            cp = cb.mapTo(window, QPoint(0, 0))
            dy = abs(cp.y() - ly)
            dx = abs(cp.x() - lp.x())
            score = dy * 1000 + dx
            txt = (cb.currentText() or "").strip().lower()
            if txt in {"it", "en", "fr", "de", "es", "pt", "auto"} or len(txt) <= 5:
                score -= 5000
            if best_score is None or score < best_score:
                best_score = score
                best_cb = cb

        target.hide()
        if best_cb is not None:
            best_cb.hide()
    except Exception:
        pass



def _normalize_lang_code(value):
    s = str(value or "").strip().lower()
    mapping = {
        "auto": "auto",
        "as source": "as_source",
        "as_source": "as_source",
        "italian": "it",
        "it": "it",
        "english": "en",
        "en": "en",
        "spanish": "es",
        "es": "es",
        "french": "fr",
        "fr": "fr",
        "german": "de",
        "de": "de",
        "portuguese": "pt",
        "pt": "pt",
    }
    return mapping.get(s, s or "auto")

def _resolve_source_language_from_ui(window):
    try:
        labels = [w for w in window.findChildren(QLabel) if w.isVisible() and w.text().strip() == "Source language"]
        combos = [w for w in window.findChildren(QComboBox) if w.isVisible()]
        if not labels or not combos:
            return "auto"

        best = None
        best_score = None
        for lab in labels:
            lp = lab.mapTo(window, QPoint(0, 0))
            for cb in combos:
                cp = cb.mapTo(window, QPoint(0, 0))
                dy = abs(cp.y() - lp.y())
                dx = abs(cp.x() - lp.x())
                score = dy * 1000 + dx

                txt = (cb.currentText() or "").strip().lower()
                data = cb.currentData()
                raw = data if data not in (None, "") else txt

                # preferisci combo con etichette umane tipo "Italian"
                if txt in {"italian", "english", "spanish", "french", "german", "portuguese"}:
                    score -= 5000
                # penalizza vecchi combo tecnici tipo "it", "en", "auto"
                if txt in {"it", "en", "es", "fr", "de", "pt", "auto"}:
                    score += 5000

                if best_score is None or score < best_score:
                    best_score = score
                    best = raw

        return _normalize_lang_code(best)
    except Exception:
        return "auto"

