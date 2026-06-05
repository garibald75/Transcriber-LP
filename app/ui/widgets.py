from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QDragEnterEvent, QDropEvent


class DropLabel(QLabel):
    def __init__(self, on_file_picked) -> None:
        super().__init__("Drop audio or video")
        self.on_file_picked = on_file_picked
        self.setObjectName("dropZone")
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.setMinimumHeight(82)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:
            self.on_file_picked(Path(urls[0].toLocalFile()))
            event.acceptProposedAction()
