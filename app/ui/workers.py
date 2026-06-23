from __future__ import annotations

import traceback

from PySide6.QtCore import QObject, QRunnable, Signal

from app.core import engine_manager
from app.core.transcriber import Transcriber, TranscriptionOptions


class WorkerSignals(QObject):
    log = Signal(str)
    error = Signal(str)
    finished = Signal(object)
    progress = Signal(int, int)
    cancelled = Signal()
    item_started = Signal(int, object)
    item_finished = Signal(int, object)
    item_failed = Signal(int, str)
    batch_finished = Signal(object)


class BaseWorker(QRunnable):
    def __init__(self) -> None:
        super().__init__()
        self.signals = WorkerSignals()

    def run(self) -> None:
        try:
            self.execute()
        except Exception as exc:
            self._handle_error(exc)

    def execute(self) -> None:
        raise NotImplementedError

    def _handle_error(self, exc: Exception) -> None:
        tb = traceback.format_exc()
        self.signals.log.emit("=== WORKER TRACEBACK ===")
        self.signals.log.emit(tb)
        message = str(exc)
        if "Operation cancelled by user." in message or "Operation cancelled before process start." in message:
            self.signals.cancelled.emit()
        else:
            self.signals.error.emit(f"{exc}\n\n{tb}")


class TranscribeWorker(BaseWorker):
    def __init__(self, options: TranscriptionOptions) -> None:
        super().__init__()
        self.options = options
        self.transcriber = Transcriber()

    def cancel(self) -> None:
        self.transcriber.cancel(log_cb=self.signals.log.emit)

    def execute(self) -> None:
        self.signals.log.emit("=== TRANSCRIBE WORKER START ===")
        self.signals.log.emit(f"Input: {self.options.input_file}")
        self.signals.log.emit(f"Model: {self.options.model_file}")
        self.signals.log.emit(f"Language: {self.options.language}")
        self.signals.log.emit(f"Output format: {self.options.output_format}")
        output = self.transcriber.transcribe(self.options, log_cb=self.signals.log.emit)
        self.signals.log.emit(f"=== TRANSCRIBE WORKER END OK === {output}")
        self.signals.finished.emit(output)


class BatchTranscribeWorker(BaseWorker):
    def __init__(self, options_list: list[TranscriptionOptions]) -> None:
        super().__init__()
        self.options_list = options_list
        self.transcriber = Transcriber()
        self.cancel_requested = False

    def cancel(self) -> None:
        self.cancel_requested = True
        self.transcriber.cancel(log_cb=self.signals.log.emit)

    def execute(self) -> None:
        results = []
        total = len(self.options_list)
        self.signals.log.emit(f"=== BATCH TRANSCRIBE START === {total} item(s)")

        for index, options in enumerate(self.options_list):
            if self.cancel_requested:
                self.signals.cancelled.emit()
                return

            self.signals.item_started.emit(index, options.input_file)
            self.signals.log.emit(f"=== BATCH ITEM {index + 1}/{total} START ===")
            self.signals.log.emit(f"Input: {options.input_file}")

            try:
                output = self.transcriber.transcribe(options, log_cb=self.signals.log.emit)
            except Exception as exc:
                message = str(exc)
                if "Operation cancelled by user." in message or "Operation cancelled before process start." in message:
                    self.signals.cancelled.emit()
                    return
                self.signals.item_failed.emit(index, message)
                self.signals.log.emit(f"=== BATCH ITEM {index + 1}/{total} FAILED === {message}")
                results.append({"input": options.input_file, "output": None, "error": message})
                continue

            self.signals.item_finished.emit(index, output)
            self.signals.log.emit(f"=== BATCH ITEM {index + 1}/{total} END OK === {output}")
            results.append({"input": options.input_file, "output": output, "error": None})

        self.signals.log.emit("=== BATCH TRANSCRIBE END ===")
        self.signals.batch_finished.emit(results)


class EngineUpdateCheckWorker(BaseWorker):
    """Check GitHub for a newer Whisper engine. Emits the release info or None."""

    def execute(self) -> None:
        try:
            info = engine_manager.update_available()
        except Exception as exc:
            # A failed update check must never disrupt the app; just log it.
            self.signals.log.emit(f"Engine update check skipped: {exc}")
            info = None
        self.signals.finished.emit(info)


class EngineUpdateWorker(BaseWorker):
    """Download and install a newer Whisper engine."""

    def __init__(self, info: dict) -> None:
        super().__init__()
        self.info = info

    def execute(self) -> None:
        version = self.info.get("version")
        self.signals.log.emit(f"=== ENGINE UPDATE START === {version}")
        installed = engine_manager.download_and_install(
            self.info, progress_cb=self.signals.progress.emit
        )
        self.signals.log.emit(f"=== ENGINE UPDATE END OK === {installed}")
        self.signals.finished.emit(installed)


class ModelUpdateCheckWorker(BaseWorker):
    """Check whether any installed model has a newer checksummed version."""

    def __init__(self, manager) -> None:
        super().__init__()
        self.manager = manager

    def execute(self) -> None:
        try:
            updates = self.manager.check_model_updates()
        except Exception as exc:
            self.signals.log.emit(f"Model update check skipped: {exc}")
            updates = []
        self.signals.finished.emit(updates)


class ModelUpdateWorker(BaseWorker):
    """Re-download the given models (fresh manifest definitions) with verification."""

    def __init__(self, manager, models: list) -> None:
        super().__init__()
        self.manager = manager
        self.models = models

    def execute(self) -> None:
        for model in self.models:
            self.signals.log.emit(f"=== MODEL UPDATE START === {model.label} ({model.filename})")
            self.manager.download_model(
                model.key, progress_cb=self.signals.progress.emit, definition=model
            )
            self.signals.log.emit(f"=== MODEL UPDATE END OK === {model.label}")
        self.signals.finished.emit([m.key for m in self.models])


class DownloadModelWorker(BaseWorker):
    def __init__(self, model_key: str, manager) -> None:
        super().__init__()
        self.model_key = model_key
        self.manager = manager

    def execute(self) -> None:
        self.signals.log.emit(f"=== DOWNLOAD MODEL START === {self.model_key}")
        path = self.manager.download_model(self.model_key, progress_cb=self.signals.progress.emit)
        self.signals.log.emit(f"=== DOWNLOAD MODEL END OK === {path}")
        self.signals.finished.emit(path)
