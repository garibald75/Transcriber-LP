from __future__ import annotations

import traceback

from PySide6.QtCore import QObject, QRunnable, Signal

from app.core.transcriber import Transcriber, TranscriptionOptions


class WorkerSignals(QObject):
    log = Signal(str)
    error = Signal(str)
    finished = Signal(object)
    progress = Signal(int, int)
    cancelled = Signal()


class TranscribeWorker(QRunnable):
    def __init__(self, options: TranscriptionOptions) -> None:
        super().__init__()
        self.options = options
        self.signals = WorkerSignals()
        self.transcriber = Transcriber()

    def cancel(self) -> None:
        self.transcriber.cancel(log_cb=self.signals.log.emit)

    def run(self) -> None:
        try:
            self.signals.log.emit("=== TRANSCRIBE WORKER START ===")
            self.signals.log.emit(f"Input: {self.options.input_file}")
            self.signals.log.emit(f"Model: {self.options.model_file}")
            self.signals.log.emit(f"Language: {self.options.language}")
            self.signals.log.emit(f"Output format: {self.options.output_format}")
            output = self.transcriber.transcribe(self.options, log_cb=self.signals.log.emit)
            self.signals.log.emit(f"=== TRANSCRIBE WORKER END OK === {output}")
            self.signals.finished.emit(output)
        except Exception as exc:
            msg = str(exc)
            tb = traceback.format_exc()
            self.signals.log.emit("=== TRANSCRIBE WORKER TRACEBACK ===")
            self.signals.log.emit(tb)
            if "Operation cancelled by user." in msg or "Operation cancelled before process start." in msg:
                self.signals.cancelled.emit()
            else:
                self.signals.error.emit(f"{exc}\n\n{tb}")


class DownloadModelWorker(QRunnable):
    def __init__(self, model_key: str, manager) -> None:
        super().__init__()
        self.model_key = model_key
        self.manager = manager
        self.signals = WorkerSignals()

    def run(self) -> None:
        try:
            self.signals.log.emit(f"=== DOWNLOAD MODEL START === {self.model_key}")
            path = self.manager.download_model(self.model_key, progress_cb=self.signals.progress.emit)
            self.signals.log.emit(f"=== DOWNLOAD MODEL END OK === {path}")
            self.signals.finished.emit(path)
        except Exception as exc:
            tb = traceback.format_exc()
            self.signals.log.emit("=== DOWNLOAD MODEL TRACEBACK ===")
            self.signals.log.emit(tb)
            self.signals.error.emit(f"{exc}\n\n{tb}")
