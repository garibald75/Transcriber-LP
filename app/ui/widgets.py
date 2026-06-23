from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent
from PySide6.QtWidgets import QGraphicsOpacityEffect, QLabel, QWidget


class DropArea(QWidget):
    """A container whose entire area accepts dropped media files.

    Children (buttons, queue, settings) live inside it; because they do not
    accept drops, Qt propagates drag events up to this widget, so the whole
    left panel is a single large drop target. While files are dragged over it,
    a highlighted overlay fades in to make the drop area obvious.
    """

    def __init__(self, on_files_picked, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.on_files_picked = on_files_picked
        self.setAcceptDrops(True)

        self._overlay = QLabel("Drop your files here", self)
        self._overlay.setObjectName("dropOverlay")
        self._overlay.setAlignment(Qt.AlignCenter)
        # Let drag events pass straight to this widget so moving the cursor over
        # the overlay never triggers spurious enter/leave flicker.
        self._overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._overlay.hide()

        self._opacity = QGraphicsOpacityEffect(self._overlay)
        self._opacity.setOpacity(0.0)
        self._overlay.setGraphicsEffect(self._opacity)
        self._fade = QPropertyAnimation(self._opacity, b"opacity", self)
        self._fade.setDuration(170)
        self._fade.setEasingCurve(QEasingCurve.Type.OutCubic)

    def resizeEvent(self, event) -> None:
        self._overlay.setGeometry(self.rect())
        super().resizeEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._show_overlay()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragLeaveEvent(self, event) -> None:
        self._hide_overlay()
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        self._hide_overlay()
        paths = [
            Path(url.toLocalFile())
            for url in event.mimeData().urls()
            if url.toLocalFile()
        ]
        if paths:
            # Order dropped files by date, oldest to newest, so multi-file drops
            # enter the queue in chronological order.
            paths.sort(key=file_date)
            self.on_files_picked(paths)
            event.acceptProposedAction()

    def _show_overlay(self) -> None:
        self._overlay.setGeometry(self.rect())
        self._overlay.raise_()
        self._overlay.show()
        self._fade.stop()
        self._fade.setStartValue(self._opacity.opacity())
        self._fade.setEndValue(1.0)
        self._fade.start()

    def _hide_overlay(self) -> None:
        self._fade.stop()
        self._opacity.setOpacity(0.0)
        self._overlay.hide()


def file_date(path: Path) -> float:
    """Best-available file date for sorting (creation time, falling back to mtime)."""
    try:
        stat = path.stat()
    except OSError:
        return 0.0
    return getattr(stat, "st_birthtime", None) or stat.st_mtime
