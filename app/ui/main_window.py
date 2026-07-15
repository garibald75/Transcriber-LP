from __future__ import annotations
import time

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QEvent, QItemSelectionModel, QObject, QSettings, Qt, QThreadPool, QTimer
from PySide6.QtGui import QAction, QActionGroup, QColor, QDesktopServices, QPainter, QPalette, QPen
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QProgressBar,
    QSizePolicy,
    QSlider,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QStyle,
    QStyleOptionButton,
    QStyledItemDelegate,
    QStyleOptionViewItem,
)
from PySide6.QtCore import QUrl

from app.core.model_manager import DEFAULT_DOWNLOAD_MODEL_KEY, MODEL_DEFS, ModelManager
from app.core.notices import THIRD_PARTY_NOTICE_TEXT
from app.core.paths import outputs_dir
from app.core.transcriber import TranscriptionOptions
from app.ui.widgets import DropArea, file_date
from app.core import engine_manager
from app.ui.workers import (
    BatchTranscribeWorker,
    DownloadModelWorker,
    EngineUpdateCheckWorker,
    EngineUpdateWorker,
    ModelUpdateCheckWorker,
    ModelUpdateWorker,
    TranscribeWorker,
)
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

DESIGN_TOKENS = {
    "radius": {
        "control": 8,
        "menu": 8,
    },
    "control": {
        "min_height": 32,
        "horizontal_padding": 12,
        "combo_arrow_width": 36,
        "combo_min_width": 190,
        "combo_popup_item_height": 32,
        "combo_popup_padding": 8,
        "settings_label_height": 15,
        "model_download_min_width": 96,
    },
}


# Glyph + palette colour key shown next to each queued file. The "done" glyph is
# the checkmark the user asked for; finished items stay in the queue rather than
# being removed.
QUEUE_STATUS_DISPLAY = {
    "queued": ("○", "muted"),
    "running": ("▶", "arrow"),
    "done": ("✓", "primary_bg"),
    "failed": ("✗", "danger_bg"),
    "cancelled": ("⊘", "muted"),
}
QUEUE_STATUS_LABEL = {
    "queued": "Queued",
    "running": "Transcribing",
    "done": "Done",
    "failed": "Failed",
    "cancelled": "Cancelled",
}


class ComboPopupHoverFilter(QObject):
    def __init__(self, view) -> None:
        super().__init__(view)
        self.view = view

    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.Type.MouseMove:
            position = event.position().toPoint() if hasattr(event, "position") else event.pos()
            index = self.view.indexAt(position)
            if index.isValid():
                self.view.setCurrentIndex(index)
                selection_model = self.view.selectionModel()
                if selection_model is not None:
                    selection_model.select(
                        index,
                        QItemSelectionModel.SelectionFlag.ClearAndSelect
                        | QItemSelectionModel.SelectionFlag.Rows,
                    )
                self.view.viewport().update()
        return super().eventFilter(watched, event)


class ComboItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.hover_bg = "#243f51"
        self.hover_text = "#ffffff"
        self.text = "#142536"

    def set_colors(self, *, hover_bg: str, hover_text: str, text: str) -> None:
        self.hover_bg = hover_bg
        self.hover_text = hover_text
        self.text = text

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index) -> None:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        is_hovered = bool(
            opt.state
            & (QStyle.StateFlag.State_MouseOver | QStyle.StateFlag.State_Selected)
        )

        if is_hovered:
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(self.hover_bg))
            painter.drawRoundedRect(opt.rect.adjusted(2, 1, -2, -1), 6, 6)
            painter.restore()
            opt.palette.setColor(QPalette.ColorRole.Text, QColor(self.hover_text))
            opt.palette.setColor(QPalette.ColorRole.HighlightedText, QColor(self.hover_text))
            opt.state &= ~QStyle.StateFlag.State_MouseOver
            opt.state &= ~QStyle.StateFlag.State_Selected
        else:
            opt.palette.setColor(QPalette.ColorRole.Text, QColor(self.text))

        super().paint(painter, opt, index)


class ComboPopupListDelegate(QStyledItemDelegate):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.hover_bg = "#c8eadf"
        self.hover_text = "#102131"
        self.text = "#142536"
        self.check = "#0aa37f"

    def set_colors(self, *, hover_bg: str, hover_text: str, text: str, check: str) -> None:
        self.hover_bg = hover_bg
        self.hover_text = hover_text
        self.text = text
        self.check = check

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index) -> None:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        is_hovered = bool(opt.state & QStyle.StateFlag.State_MouseOver)
        is_current = bool(index.data(Qt.ItemDataRole.UserRole + 1))

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        item_rect = opt.rect.adjusted(4, 3, -4, -3)
        if is_hovered:
            painter.setBrush(QColor(self.hover_bg))
            painter.drawRoundedRect(item_rect, 8, 8)

        painter.setPen(QColor(self.hover_text if is_hovered else self.text))
        text_rect = opt.rect.adjusted(16, 0, -44, 0)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, opt.text)

        if is_current:
            center_y = opt.rect.center().y()
            start_x = opt.rect.right() - 28
            painter.setPen(
                QPen(
                    QColor(self.check),
                    2,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin,
                )
            )
            painter.drawLine(start_x, center_y, start_x + 5, center_y + 5)
            painter.drawLine(start_x + 5, center_y + 5, start_x + 14, center_y - 5)

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index):
        size = super().sizeHint(option, index)
        size.setHeight(DESIGN_TOKENS["control"]["combo_popup_item_height"] + 14)
        return size


class DesignComboBox(QComboBox):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.empty_click_handler = None
        self._popup_frame = None
        self._popup_list = None
        self._popup_delegate = None
        self._popup_open = False

    def mousePressEvent(self, event) -> None:
        if self.currentData() is None and self.empty_click_handler is not None:
            self.empty_click_handler()
            return
        super().mousePressEvent(event)

    def showPopup(self) -> None:
        if self.currentData() is None and self.empty_click_handler is not None:
            self.empty_click_handler()
            return
        if self.count() == 0:
            return

        frame = self._ensure_popup_frame()
        popup_list = self._popup_list
        popup_list.clear()
        current_index = self.currentIndex()
        for row in range(self.count()):
            item = QListWidgetItem(self.itemText(row))
            item.setData(Qt.ItemDataRole.UserRole, row)
            item.setData(Qt.ItemDataRole.UserRole + 1, row == current_index)
            popup_list.addItem(item)
        popup_list.clearSelection()
        item_height = DESIGN_TOKENS["control"]["combo_popup_item_height"] + 14
        visible_rows = min(self.count(), self.maxVisibleItems())
        popup_height = max(1, visible_rows) * item_height + DESIGN_TOKENS["control"]["combo_popup_padding"] * 2

        width = max(self.width(), self.minimumWidth())
        below_left = self.mapToGlobal(self.rect().bottomLeft())
        above_left = self.mapToGlobal(self.rect().topLeft())
        screen = self.screen()
        avail = screen.availableGeometry() if screen is not None else None

        if avail is not None:
            # Never taller than the screen, and flip above the combo when there is
            # not enough room below — otherwise the popup gets clipped off-screen.
            popup_height = min(popup_height, avail.height() - 16)
            space_below = avail.bottom() - below_left.y()
            space_above = above_left.y() - avail.top()
            if popup_height <= space_below or space_below >= space_above:
                pos_y = min(below_left.y(), avail.bottom() - popup_height)
            else:
                pos_y = max(avail.top(), above_left.y() - popup_height)
            pos_x = max(avail.left(), min(below_left.x(), avail.right() - width))
        else:
            pos_x, pos_y = below_left.x(), below_left.y()

        frame.resize(width, popup_height)
        frame.setStyleSheet(self.window().styleSheet())
        frame.move(pos_x, pos_y)
        frame.show()
        frame.raise_()
        self._popup_open = True
        self.update()

    def hidePopup(self) -> None:
        if self._popup_frame is not None:
            self._popup_frame.hide()
        self._popup_open = False
        self.update()
        super().hidePopup()

    def eventFilter(self, watched, event) -> bool:
        if watched is self._popup_frame and event.type() == QEvent.Type.Hide:
            self._popup_open = False
            self.update()
        return super().eventFilter(watched, event)

    def _ensure_popup_frame(self) -> QFrame:
        if self._popup_frame is not None and self._popup_list is not None:
            return self._popup_frame

        frame = QFrame(self.window(), Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        frame.setObjectName("comboPopupFrame")
        frame.setFrameShape(QFrame.Shape.NoFrame)
        frame.setLineWidth(0)
        frame.setMidLineWidth(0)
        frame.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        frame.installEventFilter(self)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        popup_list = QListWidget(frame)
        popup_list.setObjectName("comboPopupList")
        popup_list.setFrameShape(QFrame.Shape.NoFrame)
        popup_list.setLineWidth(0)
        popup_list.setMidLineWidth(0)
        popup_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        popup_list.setMouseTracking(True)
        popup_list.viewport().setMouseTracking(True)
        popup_list.viewport().setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        popup_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        popup_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        popup_list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        popup_delegate = ComboPopupListDelegate(popup_list)
        popup_list.setItemDelegate(popup_delegate)
        popup_list.itemClicked.connect(self._select_popup_item)
        layout.addWidget(popup_list)

        self._popup_frame = frame
        self._popup_list = popup_list
        self._popup_delegate = popup_delegate
        return frame

    def _select_popup_item(self, item: QListWidgetItem) -> None:
        row = item.data(Qt.ItemDataRole.UserRole)
        if row is not None:
            self.setCurrentIndex(int(row))
        self.hidePopup()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)

        color = QColor(str(self.property("chevronColor") or "#1cc79a"))
        rect = self.rect()
        center_y = rect.center().y()
        start_x = rect.right() - 24

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(color, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        if self._popup_open:
            painter.drawLine(start_x, center_y + 2, start_x + 5, center_y - 3)
            painter.drawLine(start_x + 5, center_y - 3, start_x + 10, center_y + 2)
        else:
            painter.drawLine(start_x, center_y - 2, start_x + 5, center_y + 3)
            painter.drawLine(start_x + 5, center_y + 3, start_x + 10, center_y - 2)


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


class QueueTable(QTableWidget):
    """Queue table whose rows can be reordered by dragging.

    Only drags that start inside the table are treated as row moves; external
    file drags are ignored so they keep bubbling up to the surrounding
    DropArea panel, which stays the single drop target for adding files.
    """

    def __init__(self, rows: int, columns: int, parent=None) -> None:
        super().__init__(rows, columns, parent)
        self.row_move_handler = None
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)

    def dragEnterEvent(self, event) -> None:
        if event.source() is self:
            super().dragEnterEvent(event)
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:
        if event.source() is self:
            super().dragMoveEvent(event)
        else:
            event.ignore()

    def dropEvent(self, event) -> None:
        if event.source() is not self:
            event.ignore()
            return
        source = self.currentRow()
        index = self.indexAt(event.position().toPoint())
        if index.isValid():
            target = index.row()
            if self.dropIndicatorPosition() == QAbstractItemView.DropIndicatorPosition.BelowItem:
                target += 1
        else:
            # Dropped on the empty area below the rows: move to the end.
            target = self.rowCount()
        # Accept as a copy, NOT a move: when a drop is accepted as MoveAction,
        # QAbstractItemView.startDrag deletes the dragged row once the drag
        # returns, on top of the reorder done by the handler — the row vanished.
        event.setDropAction(Qt.DropAction.CopyAction)
        event.accept()
        if self.row_move_handler is not None:
            # Defer the reorder until the drag machinery has fully unwound, so
            # the table is never mutated in the middle of Qt's own drop handling.
            handler = self.row_move_handler
            QTimer.singleShot(0, lambda: handler(source, target))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"Transcriber-LP {APP_VERSION}")
        # Keep the window within a full-HD height (≤1050) so it fits on 1080p displays.
        self.resize(1320, 900)
        self.thread_pool = QThreadPool.globalInstance()
        self.model_manager = ModelManager()
        self.selected_file: Path | None = None
        self.batch_items: list[dict[str, object]] = []
        self.current_worker = None
        self.current_mode: str | None = None
        self.current_single_index: int | None = None
        self.batch_index_map: list[int] = []
        # Active queue sort: (column index, descending) or None for insertion order.
        self.queue_sort: tuple[int, bool] | None = None
        self.batch_total = 0
        self.batch_completed = 0
        self.current_transcript_path: Path | None = None
        self.media_loaded = False
        self.download_started_at = 0.0
        self.active_download_model_key: str | None = None
        self.auto_model_prompted = False
        self.engine_update_prompted = False
        self._engine_check_worker = None
        self.model_update_prompted = False
        self._model_check_worker = None
        self.download_buttons: list[QPushButton] = []
        self.model_settings_dialog: QDialog | None = None
        self.model_settings_list: QListWidget | None = None
        self.model_download_progress: QProgressBar | None = None
        self.model_download_status_label: QLabel | None = None
        self.settings = QSettings("Transcriber-LP", "Transcriber-LP")
        saved_theme = self.settings.value("appearance/theme", "light")
        self.theme_name = saved_theme if saved_theme in THEME_PALETTES else "light"
        self.log_auto_scroll = self._settings_bool("log/auto_scroll", True)

        self._build_ui()
        self.refresh_models()
        QTimer.singleShot(0, self.ensure_default_model_available)
        # Check for a newer Whisper engine and model updates shortly after
        # startup, in the background, so they never block launch.
        QTimer.singleShot(2500, self.check_engine_updates)
        QTimer.singleShot(4000, self.check_model_updates)

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

        settings_menu = menu_bar.addMenu("Settings")
        model_settings_action = QAction("Model downloads...", self)
        model_settings_action.triggered.connect(self.show_model_settings)
        settings_menu.addAction(model_settings_action)
        engine_update_action = QAction("Check for Whisper engine updates...", self)
        engine_update_action.triggered.connect(lambda: self.check_engine_updates(manual=True))
        settings_menu.addAction(engine_update_action)
        model_update_action = QAction("Check for model updates...", self)
        model_update_action.triggered.connect(lambda: self.check_model_updates(manual=True))
        settings_menu.addAction(model_update_action)

        help_menu = menu_bar.addMenu("Help")
        help_action = QAction("Show manual", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        security_action = QAction("macOS security & permissions...", self)
        security_action.triggered.connect(self.show_security_help)
        help_menu.addAction(security_action)
        licenses_action = QAction("Open-source licenses", self)
        licenses_action.triggered.connect(self.show_open_source_notices)
        help_menu.addAction(licenses_action)
        about_action = QAction(f"About Transcriber-LP {APP_VERSION}", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        central = QWidget()
        central.setObjectName("appRoot")
        root = QVBoxLayout(central)
        root.setContentsMargins(22, 10, 22, 16)
        root.setSpacing(6)

        header = QWidget()
        header.setObjectName("header")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)

        title = QLabel("Transcriber-LP")
        title.setObjectName("appTitle")
        header_layout.addWidget(title)
        root.addWidget(header)

        splitter = QSplitter()
        splitter.setObjectName("mainSplitter")
        splitter.setChildrenCollapsible(False)
        root.addWidget(splitter, stretch=1)
        self.setCentralWidget(central)

        # The whole left panel is the drop target — drag files anywhere over it.
        left = DropArea(self.enqueue_paths)
        left.setMinimumWidth(360)
        left.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 14, 0)
        left_layout.setSpacing(6)

        self.browse_btn = QPushButton("Add or Drop files here")
        self.browse_btn.setObjectName("browseButton")
        self.browse_btn.setProperty("role", "secondary")
        self.browse_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        self.browse_btn.clicked.connect(self.browse_file)
        self.browse_btn.setToolTip("Add one or more media files to the queue: pick them, or drag and drop them anywhere on this panel.")
        left_layout.addWidget(self.browse_btn)

        batch_box = QGroupBox("Queue")
        batch_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        batch_layout = QVBoxLayout(batch_box)
        batch_layout.setContentsMargins(16, 16, 16, 12)
        batch_layout.setSpacing(6)

        self.batch_list = QueueTable(0, 3)
        self.batch_list.setObjectName("queueTable")
        self.batch_list.row_move_handler = self.move_queue_row
        self.batch_list.setHorizontalHeaderLabels(["File", "Date", "Status"])
        self.batch_list.setMinimumHeight(64)
        self.batch_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.batch_list.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.batch_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.batch_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.batch_list.setShowGrid(False)
        self.batch_list.setWordWrap(False)
        self.batch_list.verticalHeader().setVisible(False)
        header = self.batch_list.horizontalHeader()
        header.setHighlightSections(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self.on_queue_header_clicked)
        self.batch_list.itemSelectionChanged.connect(self.on_batch_selection_changed)
        self.batch_list.itemDoubleClicked.connect(lambda _item: self.retrieve_batch_output())
        self.batch_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.batch_list.customContextMenuRequested.connect(self.show_queue_context_menu)
        self.batch_list.setToolTip(
            "Loaded media files. Click a column header to sort, or drag rows to reorder. "
            "Completed files stay here with a ✓ checkmark."
        )
        batch_layout.addWidget(self.batch_list, stretch=1)

        batch_row_one = QHBoxLayout()
        batch_row_one.setSpacing(8)
        self.remove_batch_btn = QPushButton("Remove")
        self.remove_batch_btn.setProperty("role", "secondary")
        self.remove_batch_btn.clicked.connect(self.remove_selected_batch_item)
        self.remove_batch_btn.setEnabled(False)
        self.remove_batch_btn.setToolTip("Remove the selected item from the queue.")
        batch_row_one.addWidget(self.remove_batch_btn)

        self.move_up_btn = QPushButton()
        self.move_up_btn.setObjectName("iconButton")
        self.move_up_btn.setProperty("role", "secondary")
        self.move_up_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp))
        self.move_up_btn.clicked.connect(lambda: self.move_selected_queue_item(-1))
        self.move_up_btn.setEnabled(False)
        self.move_up_btn.setFixedWidth(42)
        self.move_up_btn.setToolTip("Move the selected file up in the queue. You can also drag rows to reorder.")
        batch_row_one.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton()
        self.move_down_btn.setObjectName("iconButton")
        self.move_down_btn.setProperty("role", "secondary")
        self.move_down_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown))
        self.move_down_btn.clicked.connect(lambda: self.move_selected_queue_item(1))
        self.move_down_btn.setEnabled(False)
        self.move_down_btn.setFixedWidth(42)
        self.move_down_btn.setToolTip("Move the selected file down in the queue. You can also drag rows to reorder.")
        batch_row_one.addWidget(self.move_down_btn)

        batch_row_one.addStretch(1)

        self.clear_done_btn = QPushButton()
        self.clear_done_btn.setObjectName("iconButton")
        self.clear_done_btn.setProperty("role", "secondary")
        self.clear_done_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
        self.clear_done_btn.clicked.connect(self.clear_done_items)
        self.clear_done_btn.setEnabled(False)
        self.clear_done_btn.setFixedWidth(42)
        self.clear_done_btn.setToolTip("Clear done — remove completed (✓) files from the queue.")
        batch_row_one.addWidget(self.clear_done_btn)

        self.clear_batch_btn = QPushButton()
        self.clear_batch_btn.setObjectName("iconButton")
        self.clear_batch_btn.setProperty("role", "secondary")
        self.clear_batch_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        self.clear_batch_btn.clicked.connect(self.clear_batch_queue)
        self.clear_batch_btn.setEnabled(False)
        self.clear_batch_btn.setFixedWidth(42)
        self.clear_batch_btn.setToolTip("Clear all — remove every file from the queue.")
        batch_row_one.addWidget(self.clear_batch_btn)
        batch_layout.addLayout(batch_row_one)

        batch_row_two = QHBoxLayout()
        batch_row_two.setSpacing(8)
        self.batch_transcribe_btn = QPushButton("Transcribe queue")
        self.batch_transcribe_btn.setProperty("role", "primary")
        self.batch_transcribe_btn.clicked.connect(self.start_batch_transcription)
        self.batch_transcribe_btn.setEnabled(False)
        self.batch_transcribe_btn.setToolTip("Transcribe every not-yet-done file in the queue sequentially.")
        batch_row_two.addWidget(self.batch_transcribe_btn)

        self.retrieve_batch_btn = QPushButton("Retrieve output")
        self.retrieve_batch_btn.setProperty("role", "secondary")
        self.retrieve_batch_btn.clicked.connect(self.retrieve_batch_output)
        self.retrieve_batch_btn.setEnabled(False)
        self.retrieve_batch_btn.setToolTip("Open the selected completed output in the transcript editor.")
        batch_row_two.addWidget(self.retrieve_batch_btn)
        batch_layout.addLayout(batch_row_two)

        left_layout.addWidget(batch_box, stretch=2)

        settings_box = QGroupBox("⚙ Settings")
        settings_layout = QVBoxLayout(settings_box)
        settings_layout.setContentsMargins(16, 16, 16, 12)
        settings_layout.setSpacing(8)

        def settings_label(text: str) -> QLabel:
            label = QLabel(text)
            label.setProperty("role", "settingsLabel")
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            label.setMinimumHeight(DESIGN_TOKENS["control"]["settings_label_height"])
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            return label

        def add_settings_row(text: str, field: QWidget) -> None:
            field_group = QWidget()
            field_group.setObjectName("settingsFieldGroup")
            field_group_layout = QVBoxLayout(field_group)
            field_group_layout.setContentsMargins(0, 0, 0, 0)
            field_group_layout.setSpacing(4)
            field_group_layout.addWidget(settings_label(text))
            field_group_layout.addWidget(field)
            settings_layout.addWidget(field_group)

        self.output_combo = DesignComboBox()
        self.output_combo.addItems(["txt", "srt", "vtt"])
        self.output_combo.setToolTip("Choose the output subtitle/text format for the transcription.")
        add_settings_row("Output format", self.output_combo)
        self.save_timestamps_checkbox = XCheckBox("Timestamped output")
        self.save_timestamps_checkbox.setMinimumHeight(DESIGN_TOKENS["control"]["min_height"])
        self.save_timestamps_checkbox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.save_timestamps_checkbox.setChecked(self._settings_bool("export/save_timestamps", False))
        self.save_timestamps_checkbox.setToolTip(
            "For TXT, add timecodes to each transcript line. SRT and VTT already include timecodes. Also saves a CSV sidecar."
        )
        self.save_timestamps_checkbox.toggled.connect(
            lambda enabled: self.settings.setValue("export/save_timestamps", enabled)
        )
        add_settings_row("Timestamp output", self.save_timestamps_checkbox)

        self.model_combo = DesignComboBox()
        self.model_combo.empty_click_handler = self.show_model_settings
        self.model_combo.setToolTip("Current transcription model. If none is installed, click to open model downloads.")
        self.source_language_combo = DesignComboBox()
        self.source_language_combo.addItem("Auto-detect", "auto")
        self.source_language_combo.addItem("Italian", "it")
        self.source_language_combo.addItem("English", "en")
        self.source_language_combo.addItem("Spanish", "es")
        self.source_language_combo.addItem("Portuguese", "pt")
        self.source_language_combo.addItem("French", "fr")
        self.source_language_combo.addItem("German", "de")
        self.source_language_combo.setToolTip("Force the source language for transcription, or use auto-detection.")
        self.target_language_combo = DesignComboBox()
        self.target_language_combo.addItem("Keep original language", "as_source")
        self.target_language_combo.addItem("Translate to English", "english")
        self.target_language_combo.setToolTip("Choose whether to keep the original language or translate the transcript into English.")
        self.styled_combos = []
        for combo in (
            self.output_combo,
            self.model_combo,
            self.source_language_combo,
            self.target_language_combo,
        ):
            self._configure_combo(combo)

        add_settings_row("Current Model", self.model_combo)
        add_settings_row("Source language", self.source_language_combo)
        add_settings_row("Translation target", self.target_language_combo)

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

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setProperty("role", "secondary")
        self.reset_btn.clicked.connect(self.reset_workspace)
        self.reset_btn.setToolTip(
            "Start a new session: clear the queue, media preview, transcript editor and progress. "
            "Output files already saved on disk are not affected."
        )
        button_row.addWidget(self.reset_btn)
        left_layout.addLayout(button_row)

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
        right.setMinimumWidth(520)
        right.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(14, 0, 0, 0)
        right_layout.setSpacing(6)

        review_splitter = QSplitter(Qt.Orientation.Vertical)
        review_splitter.setObjectName("reviewSplitter")
        review_splitter.setChildrenCollapsible(False)
        right_layout.addWidget(review_splitter, stretch=1)

        media_box = QGroupBox("Media Preview")
        media_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        media_layout = QVBoxLayout(media_box)
        media_layout.setContentsMargins(16, 20, 16, 14)
        media_layout.setSpacing(8)
        self.video_widget = QVideoWidget()
        self.video_widget.setObjectName("videoPreview")
        self.video_widget.setMinimumHeight(70)
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        media_layout.addWidget(self.video_widget, stretch=1)

        player_row = QHBoxLayout()
        player_row.setSpacing(8)
        self.play_pause_btn = QPushButton("Play")
        self.play_pause_btn.setProperty("role", "secondary")
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_pause_btn.setEnabled(False)
        self.play_pause_btn.clicked.connect(self.toggle_playback)
        self.play_pause_btn.setToolTip("Play or pause the selected source media.")
        player_row.addWidget(self.play_pause_btn)

        self.media_stop_btn = QPushButton("Stop")
        self.media_stop_btn.setProperty("role", "secondary")
        self.media_stop_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.media_stop_btn.setEnabled(False)
        self.media_stop_btn.clicked.connect(self.stop_media)
        self.media_stop_btn.setToolTip("Stop media playback.")
        player_row.addWidget(self.media_stop_btn)

        self.position_label = QLabel("00:00")
        self.position_label.setObjectName("timeLabel")
        player_row.addWidget(self.position_label)

        self.media_slider = QSlider(Qt.Orientation.Horizontal)
        self.media_slider.setEnabled(False)
        self.media_slider.setRange(0, 0)
        self.media_slider.sliderMoved.connect(self.seek_media)
        self.media_slider.setToolTip("Seek through the selected source media.")
        player_row.addWidget(self.media_slider, stretch=1)

        self.duration_label = QLabel("00:00")
        self.duration_label.setObjectName("timeLabel")
        player_row.addWidget(self.duration_label)
        media_layout.addLayout(player_row)
        review_splitter.addWidget(media_box)

        self.audio_output = QAudioOutput(self)
        self.media_player = QMediaPlayer(self)
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.durationChanged.connect(self.on_media_duration_changed)
        self.media_player.positionChanged.connect(self.on_media_position_changed)
        self.media_player.playbackStateChanged.connect(self.on_playback_state_changed)
        self.media_player.errorOccurred.connect(self.on_media_error)

        editor_box = QGroupBox("Transcript Editor")
        editor_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        editor_layout = QVBoxLayout(editor_box)
        editor_layout.setContentsMargins(16, 20, 16, 14)
        editor_layout.setSpacing(8)
        editor_header = QHBoxLayout()
        editor_header.setContentsMargins(0, 0, 0, 0)
        self.transcript_label = QLabel("No transcript loaded")
        self.transcript_label.setObjectName("transcriptLabel")
        self.transcript_label.setWordWrap(True)
        editor_header.addWidget(self.transcript_label, stretch=1)

        self.open_transcript_btn = QPushButton("Open transcript")
        self.open_transcript_btn.setProperty("role", "secondary")
        self.open_transcript_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        self.open_transcript_btn.clicked.connect(self.open_transcript_file)
        self.open_transcript_btn.setToolTip("Open an existing transcript file for quick corrections.")
        editor_header.addWidget(self.open_transcript_btn)

        self.save_transcript_btn = QPushButton("Save changes")
        self.save_transcript_btn.setProperty("role", "primary")
        self.save_transcript_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.save_transcript_btn.setEnabled(False)
        self.save_transcript_btn.clicked.connect(self.save_transcript)
        self.save_transcript_btn.setToolTip("Save the corrected transcript back to the loaded file.")
        editor_header.addWidget(self.save_transcript_btn)
        editor_layout.addLayout(editor_header)

        self.transcript_editor = QPlainTextEdit()
        self.transcript_editor.setObjectName("transcriptEditor")
        self.transcript_editor.setPlaceholderText("Completed transcripts open here for quick correction.")
        self.transcript_editor.setEnabled(False)
        self.transcript_editor.setMinimumHeight(60)
        self.transcript_editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.transcript_editor.setToolTip("Edit the generated txt, srt, or vtt transcript.")
        editor_layout.addWidget(self.transcript_editor, stretch=1)
        review_splitter.addWidget(editor_box)

        log_panel = QWidget()
        log_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        log_panel_layout = QVBoxLayout(log_panel)
        log_panel_layout.setContentsMargins(0, 0, 0, 0)
        log_panel_layout.setSpacing(8)
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
        log_panel_layout.addLayout(log_header)
        self.log = QPlainTextEdit()
        self.log.setObjectName("logPanel")
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(54)
        self.log.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.log.setToolTip("Detailed log output from transcription and downloads.")
        log_panel_layout.addWidget(self.log, stretch=1)
        review_splitter.addWidget(log_panel)
        review_splitter.setSizes([320, 230, 130])
        review_splitter.setStretchFactor(0, 5)
        review_splitter.setStretchFactor(1, 3)
        review_splitter.setStretchFactor(2, 2)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([540, 780])
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        self.set_theme(self.theme_name, persist=False)
        self.sync_action_controls()

    def enqueue_paths(self, paths) -> list[Path]:
        """Add one or more media files to the queue and select the first new one.

        Used by drag-and-drop and the "Add or Drop files here" picker so every
        loaded file lives in a single queue and stays there with a status glyph.
        """
        known_paths = {str(item["path"]) for item in self.batch_items}
        added: list[Path] = []
        for raw in paths:
            path = Path(raw)
            if str(path) in known_paths:
                continue
            self.batch_items.append({"path": path, "status": "queued", "output": None, "error": None})
            known_paths.add(str(path))
            added.append(path)

        self.refresh_batch_list()
        if added:
            first_new = str(added[0])
            for row, item in enumerate(self.batch_items):
                if str(item["path"]) == first_new:
                    self._select_queue_row(row)
                    break
            self.append_log(f"Added {len(added)} file(s) to the queue.")
        elif paths:
            self.append_log("File(s) already in the queue.")
        return added

    def _select_queue_row(self, row: int) -> None:
        if not (0 <= row < len(self.batch_items)):
            return
        self.batch_list.blockSignals(True)
        self.batch_list.setCurrentCell(row, 0)
        self.batch_list.blockSignals(False)
        path = Path(self.batch_items[row]["path"])
        self.selected_file = path
        if path.exists():
            self.load_media(path)
        self.sync_action_controls()

    def browse_file(self) -> None:
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Pick media files",
            str(Path.home()),
            "Media files (*.mp4 *.mov *.mkv *.avi *.mp3 *.wav *.m4a *.aac *.flac);;All files (*.*)",
        )
        if file_paths:
            self.enqueue_paths([Path(p) for p in file_paths])

    def show_queue_context_menu(self, pos) -> None:
        row = self.batch_list.rowAt(pos.y())
        if not (0 <= row < len(self.batch_items)):
            return
        self._select_queue_row(row)
        can_reorder = self.current_worker is None and len(self.batch_items) > 1
        menu = QMenu(self.batch_list)
        move_up_action = menu.addAction("Sposta su")
        move_up_action.setEnabled(can_reorder and row > 0)
        move_down_action = menu.addAction("Sposta giù")
        move_down_action.setEnabled(can_reorder and row < len(self.batch_items) - 1)
        menu.addSeparator()
        info_action = menu.addAction("Informazioni file")
        chosen = menu.exec(self.batch_list.viewport().mapToGlobal(pos))
        if chosen is info_action:
            self.show_file_info(row)
        elif chosen is move_up_action:
            self.move_selected_queue_item(-1)
        elif chosen is move_down_action:
            self.move_selected_queue_item(1)

    def show_file_info(self, row: int) -> None:
        if not (0 <= row < len(self.batch_items)):
            return
        item = self.batch_items[row]
        path = Path(item["path"])
        status_label = QUEUE_STATUS_LABEL.get(str(item.get("status") or "queued"), "—")
        lines = [
            f"Nome: {path.name}",
            f"Percorso: {path}",
            f"Stato: {status_label}",
        ]
        ts = self._queue_timestamp(item)
        if ts:
            lines.append(f"Data: {datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')}")
        try:
            size = path.stat().st_size
            lines.append(f"Dimensione: {_format_bytes(size)}")
        except OSError:
            lines.append("Dimensione: file non trovato")
        if item.get("output"):
            lines.append(f"Output: {Path(item['output']).name}")
        if item.get("error"):
            lines.append(f"Errore: {item['error']}")
        QMessageBox.information(self, "Informazioni file", "\n".join(lines))

    def move_queue_row(self, source: int, target: int) -> None:
        """Move a queue item from row `source` to insertion index `target`.

        Blocked while any worker runs, because in-flight batch progress relies
        on stable row <-> batch_items indices.
        """
        if self.current_worker is not None:
            return
        count = len(self.batch_items)
        if not (0 <= source < count):
            return
        if source < target:
            target -= 1
        target = max(0, min(target, count - 1))
        if target == source:
            return
        item = self.batch_items.pop(source)
        self.batch_items.insert(target, item)
        # Manual order replaces any active header sort.
        self.queue_sort = None
        self.batch_list.horizontalHeader().setSortIndicatorShown(False)
        self.refresh_batch_list()
        self._select_queue_row(target)
        self.append_log(f"Moved in queue: {Path(item['path']).name} → position {target + 1}")

    def move_selected_queue_item(self, delta: int) -> None:
        row = self.batch_list.currentRow()
        if not (0 <= row < len(self.batch_items)):
            return
        target = row + delta
        if not (0 <= target < len(self.batch_items)):
            return
        # move_queue_row expects an insertion index, so moving down inserts
        # after the row below.
        self.move_queue_row(row, target if delta < 0 else target + 1)

    def remove_selected_batch_item(self) -> None:
        row = self.batch_list.currentRow()
        if row < 0 or row >= len(self.batch_items):
            return
        removed = self.batch_items.pop(row)
        self.refresh_batch_list()
        self.append_log(f"Removed from queue: {removed['path']}")

    def clear_done_items(self) -> None:
        before = len(self.batch_items)
        self.batch_items = [item for item in self.batch_items if item.get("status") != "done"]
        removed = before - len(self.batch_items)
        self.refresh_batch_list()
        self.append_log(f"Cleared {removed} completed item(s) from the queue.")

    def clear_batch_queue(self) -> None:
        self.batch_items.clear()
        self.refresh_batch_list()
        self.append_log("Queue cleared.")

    def reset_workspace(self) -> None:
        """Return the UI to a fresh-session state: empty queue, no media, no transcript."""
        if self.current_worker is not None:
            return
        has_content = (
            bool(self.batch_items)
            or self.current_transcript_path is not None
            or bool(self.transcript_editor.toPlainText())
        )
        if has_content and not self._confirm_reset():
            self.append_log("Workspace reset cancelled.")
            return

        self.media_player.stop()
        self.media_player.setSource(QUrl())
        self.media_loaded = False
        self.media_slider.setRange(0, 0)
        self.media_slider.setValue(0)
        self.position_label.setText("00:00")
        self.duration_label.setText("00:00")
        self.play_pause_btn.setText("Play")
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

        self.batch_items.clear()
        self.queue_sort = None
        self.batch_list.horizontalHeader().setSortIndicatorShown(False)
        self.batch_index_map = []
        self.batch_total = 0
        self.batch_completed = 0
        self.current_single_index = None
        self.selected_file = None

        self.current_transcript_path = None
        self.transcript_editor.clear()
        self.transcript_editor.setEnabled(False)
        self.transcript_label.setText("No transcript loaded")

        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress.setFormat("%p%")
        self.progress_label.setText("Ready")
        self.refresh_batch_list()
        self.append_log("Workspace reset for a new session.")

    def _confirm_reset(self) -> bool:
        confirm = QMessageBox(self)
        confirm.setIcon(QMessageBox.Icon.Question)
        confirm.setWindowTitle("Reset workspace?")
        confirm.setText("Reset clears the queue, the media preview and the transcript editor.")
        confirm.setInformativeText("Output files already saved on disk are not affected.\n\nContinue?")
        reset_button = confirm.addButton("Reset", QMessageBox.ButtonRole.AcceptRole)
        confirm.addButton(QMessageBox.StandardButton.Cancel)
        confirm.setDefaultButton(QMessageBox.StandardButton.Cancel)
        confirm.exec()
        return confirm.clickedButton() is reset_button

    def refresh_batch_list(self) -> None:
        current_row = self.batch_list.currentRow()
        colors = THEME_PALETTES[self.theme_name]
        text_color = QColor(colors["list_text"])
        self.batch_list.blockSignals(True)
        self.batch_list.setRowCount(len(self.batch_items))
        for row, item in enumerate(self.batch_items):
            path = Path(item["path"])
            status = str(item.get("status") or "queued")
            glyph, color_key = QUEUE_STATUS_DISPLAY.get(status, QUEUE_STATUS_DISPLAY["queued"])
            row_color = QColor(colors.get(color_key, colors["list_text"]))
            output = item.get("output")
            suffix = f"  →  {Path(output).name}" if output else ""
            status_label = QUEUE_STATUS_LABEL.get(status, status)
            tooltip = f"{status_label} — {path}"
            if item.get("error"):
                tooltip += f"\n{item['error']}"

            file_cell = self._queue_cell(f"{glyph}  {path.name}{suffix}", row_color, tooltip)
            date_cell = self._queue_cell(self._queue_date_text(item), text_color, tooltip)
            status_cell = self._queue_cell(status_label, row_color, tooltip)
            self.batch_list.setItem(row, 0, file_cell)
            self.batch_list.setItem(row, 1, date_cell)
            self.batch_list.setItem(row, 2, status_cell)

        if self.batch_items:
            self.batch_list.setCurrentCell(
                max(0, min(current_row, len(self.batch_items) - 1)), 0
            )
        self.batch_list.blockSignals(False)
        self.sync_action_controls()

    def _queue_cell(self, text: str, color: QColor, tooltip: str) -> QTableWidgetItem:
        cell = QTableWidgetItem(text)
        cell.setForeground(color)
        cell.setToolTip(tooltip)
        return cell

    def _queue_timestamp(self, item: dict) -> float:
        """Cached file date used for both display and date-column sorting."""
        ts = item.get("date_ts")
        if ts is None:
            ts = file_date(Path(item["path"]))
            item["date_ts"] = ts
        return ts

    def _queue_date_text(self, item: dict) -> str:
        ts = self._queue_timestamp(item)
        if not ts:
            return "—"
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")

    def on_queue_header_clicked(self, column: int) -> None:
        # Reorder the underlying queue so the row<->batch_items index mapping the
        # rest of the code relies on stays intact. Disabled mid-run to avoid
        # invalidating the in-flight batch index map.
        if self.current_worker is not None or not self.batch_items:
            return

        descending = False
        if self.queue_sort and self.queue_sort[0] == column:
            descending = not self.queue_sort[1]
        self.queue_sort = (column, descending)

        selected_path = None
        row = self.batch_list.currentRow()
        if 0 <= row < len(self.batch_items):
            selected_path = str(self.batch_items[row]["path"])

        if column == 1:
            key = self._queue_timestamp
        elif column == 2:
            order = list(QUEUE_STATUS_LABEL.keys())
            key = lambda it: order.index(str(it.get("status") or "queued")) if str(it.get("status") or "queued") in order else len(order)
        else:
            key = lambda it: Path(it["path"]).name.lower()
        self.batch_items.sort(key=key, reverse=descending)

        self.batch_list.horizontalHeader().setSortIndicator(
            column, Qt.SortOrder.DescendingOrder if descending else Qt.SortOrder.AscendingOrder
        )
        self.batch_list.horizontalHeader().setSortIndicatorShown(True)

        self.refresh_batch_list()
        if selected_path is not None:
            for new_row, item in enumerate(self.batch_items):
                if str(item["path"]) == selected_path:
                    self._select_queue_row(new_row)
                    break

    def on_batch_selection_changed(self) -> None:
        row = self.batch_list.currentRow()
        if 0 <= row < len(self.batch_items):
            path = Path(self.batch_items[row]["path"])
            self.selected_file = path
            if path.exists():
                self.load_media(path)
        self.sync_action_controls()

    def sync_batch_controls(self) -> None:
        self.sync_action_controls()

    def sync_action_controls(self) -> None:
        has_items = bool(self.batch_items)
        has_done = any(item.get("status") == "done" for item in self.batch_items)
        has_pending = any(item.get("status") != "done" for item in self.batch_items)
        row = self.batch_list.currentRow()
        has_selection = 0 <= row < len(self.batch_items)
        selected_output = self.batch_items[row].get("output") if has_selection else None
        is_busy = self.current_worker is not None
        is_transcribing = is_busy and self.current_mode in {"single", "batch"}
        has_file = self.selected_file is not None
        has_model = self.current_model_key() is not None
        has_transcript = self.current_transcript_path is not None
        media_can_stop = (
            self.media_loaded
            and self.media_player.playbackState() != QMediaPlayer.PlaybackState.StoppedState
        )

        self.browse_btn.setEnabled(not is_busy)
        self.transcribe_btn.setText("Transcribe selected" if has_selection else "Transcribe")
        self.transcribe_btn.setToolTip(
            "Transcribe only the file selected in the queue."
            if has_selection
            else "Start the transcription process for the selected file."
        )
        self.transcribe_btn.setEnabled(has_file and has_model and not is_busy)
        self.stop_btn.setEnabled(is_transcribing)
        self.open_output_btn.setEnabled(not is_busy)
        self.open_transcript_btn.setEnabled(not is_busy)
        self.save_transcript_btn.setEnabled(has_transcript and self.transcript_editor.isEnabled() and not is_busy)
        self.output_combo.setEnabled(not is_busy)
        self.model_combo.setEnabled(not is_busy)
        self.source_language_combo.setEnabled(not is_busy)
        self.target_language_combo.setEnabled(not is_busy)
        self.save_timestamps_checkbox.setEnabled(not is_busy)
        self.remove_batch_btn.setEnabled(has_selection and not is_busy)
        can_reorder = has_selection and len(self.batch_items) > 1 and not is_busy
        self.move_up_btn.setEnabled(can_reorder and row > 0)
        self.move_down_btn.setEnabled(can_reorder and row < len(self.batch_items) - 1)
        self.batch_list.setDragEnabled(can_reorder)
        self.reset_btn.setEnabled(not is_busy)
        self.clear_done_btn.setEnabled(has_done and not is_busy)
        self.clear_batch_btn.setEnabled(has_items and not is_busy)
        self.batch_transcribe_btn.setEnabled(has_pending and has_model and not is_busy)
        self.retrieve_batch_btn.setEnabled(bool(selected_output) and not is_busy)
        self.play_pause_btn.setEnabled(self.media_loaded)
        self.media_stop_btn.setEnabled(media_can_stop)
        self.media_slider.setEnabled(self.media_loaded)
        self._set_download_controls_enabled(not is_busy)
        self._sync_button_cursors()

    def start_batch_transcription(self) -> None:
        # Only transcribe files that are not already done, so completed (✓) items
        # stay in the queue without being re-run.
        pending = [
            index for index, item in enumerate(self.batch_items)
            if item.get("status") != "done"
        ]
        if not pending:
            if self.batch_items:
                QMessageBox.information(self, "Nothing to do", "Every file in the queue is already transcribed.")
            else:
                QMessageBox.warning(self, "Missing files", "Add or drop files into the queue first.")
            return

        model_key = self.current_model_key()
        if model_key is None:
            self.ensure_default_model_available(force=True)
            return

        try:
            model_file = self.model_manager.resolve_model_path(model_key)
        except Exception as exc:
            QMessageBox.critical(self, "Model error", str(exc))
            return

        output_dir = self._choose_output_dir("Select batch output folder")
        if not output_dir:
            return

        stem_counts = _count_stems([Path(self.batch_items[i]["path"]) for i in pending])
        options_list: list[TranscriptionOptions] = []
        self.batch_index_map = pending
        for position, index in enumerate(pending):
            item = self.batch_items[index]
            path = Path(item["path"])
            item["status"] = "queued"
            item["output"] = None
            item["error"] = None
            options_list.append(
                TranscriptionOptions(
                    input_file=path,
                    model_file=model_file,
                    language=self.source_language_combo.currentData() or "auto",
                    output_format=self.output_combo.currentText(),
                    target_language=self.target_language_combo.currentData() or "as_source",
                    save_timestamps=self.save_timestamps_checkbox.isChecked(),
                    output_name=_batch_output_name(path, position, stem_counts),
                    output_dir=output_dir,
                )
            )

        self.refresh_batch_list()
        self.batch_total = len(options_list)
        self.batch_completed = 0
        self.progress.setRange(0, self.batch_total)
        self.progress.setValue(0)
        self.progress.setFormat("%v / %m")
        self.progress_label.setText(f"Transcribing queue: 0/{self.batch_total} done")
        self.append_log(f"Starting queue transcription: {self.batch_total} file(s)")

        worker = BatchTranscribeWorker(options_list)
        worker.signals.log.connect(self.append_log)
        worker.signals.error.connect(self.on_worker_error)
        worker.signals.cancelled.connect(self.on_batch_cancelled)
        worker.signals.item_started.connect(self.on_batch_item_started)
        worker.signals.item_finished.connect(self.on_batch_item_finished)
        worker.signals.item_failed.connect(self.on_batch_item_failed)
        worker.signals.batch_finished.connect(self.on_batch_finished)
        self.current_worker = worker
        self.current_mode = "batch"
        self.sync_action_controls()
        self.thread_pool.start(worker)

    def _batch_item_index(self, worker_index: int) -> int:
        if 0 <= worker_index < len(self.batch_index_map):
            return self.batch_index_map[worker_index]
        return worker_index

    def on_batch_item_started(self, index: int, input_path) -> None:
        actual = self._batch_item_index(index)
        self.batch_items[actual]["status"] = "running"
        self.refresh_batch_list()
        self._select_queue_row(actual)
        self.progress_label.setText(
            f"Transcribing {self.batch_completed + 1}/{self.batch_total}: {Path(input_path).name}"
        )

    def on_batch_item_finished(self, index: int, output_path) -> None:
        actual = self._batch_item_index(index)
        output_path = Path(output_path)
        self.batch_items[actual]["status"] = "done"
        self.batch_items[actual]["output"] = output_path
        self.batch_items[actual]["error"] = None
        self.batch_completed += 1
        self.progress.setValue(self.batch_completed)
        self.refresh_batch_list()
        self._select_queue_row(actual)
        self.load_transcript(output_path)
        self.progress_label.setText(f"Transcribing queue: {self.batch_completed}/{self.batch_total} done")

    def on_batch_item_failed(self, index: int, message: str) -> None:
        actual = self._batch_item_index(index)
        self.batch_items[actual]["status"] = "failed"
        self.batch_items[actual]["error"] = message
        self.batch_completed += 1
        self.progress.setValue(self.batch_completed)
        self.refresh_batch_list()
        self._select_queue_row(actual)
        self.append_log(f"Queue item failed: {self.batch_items[actual]['path']} :: {message}")

    def on_batch_finished(self, results) -> None:
        completed = sum(1 for item in self.batch_items if item.get("status") == "done")
        failed = sum(1 for item in self.batch_items if item.get("status") == "failed")
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.progress.setFormat("Done")
        self.progress_label.setText(f"Queue complete: {completed} done, {failed} failed")
        self.append_log(f"Queue complete: {completed} done, {failed} failed")
        QMessageBox.information(self, "Queue completed", f"Completed: {completed}\nFailed: {failed}")
        self.current_worker = None
        self.current_mode = None
        self.sync_action_controls()

    def on_batch_cancelled(self) -> None:
        self.append_log("Batch transcription cancelled.")
        for item in self.batch_items:
            if item.get("status") == "running":
                item["status"] = "cancelled"
        self.refresh_batch_list()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress_label.setText("Batch cancelled")
        self.current_worker = None
        self.current_mode = None
        self.sync_action_controls()

    def retrieve_batch_output(self) -> None:
        row = self.batch_list.currentRow()
        if row < 0 or row >= len(self.batch_items):
            return
        item = self.batch_items[row]
        output = item.get("output")
        if not output:
            QMessageBox.information(self, "No output", "The selected batch item has no completed output yet.")
            return
        output_path = Path(output)
        if not output_path.exists():
            QMessageBox.warning(self, "Missing output", f"Output file not found:\n{output_path}")
            return
        self.selected_file = Path(item["path"])
        self.load_media(Path(item["path"]))
        self.load_transcript(output_path)
        self.append_log(f"Retrieved batch output: {output_path}")

    def refresh_models(self) -> None:
        self.model_combo.clear()
        items = self.model_manager.available_models()
        medium_index = -1
        for idx, (key, path, source) in enumerate(items):
            display = MODEL_DEFS.get(key).label if key in MODEL_DEFS else key
            self.model_combo.addItem(f"{display} ({source})", userData=key)
            if key == "medium":
                medium_index = idx

        if medium_index >= 0:
            self.model_combo.setCurrentIndex(medium_index)

        if not items:
            self.model_combo.addItem("click here to download a model", userData=None)
            self.model_combo.setCurrentIndex(0)

        self.refresh_model_settings_list()
        self.sync_action_controls()

    def current_model_key(self) -> str | None:
        key = self.model_combo.currentData()
        return str(key) if key else None

    def show_model_settings(self) -> None:
        dialog = self._ensure_model_settings_dialog()
        self.refresh_model_settings_list()
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    def _ensure_model_settings_dialog(self) -> QDialog:
        if self.model_settings_dialog is not None:
            return self.model_settings_dialog

        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setMinimumWidth(420)
        dialog.setObjectName("settingsDialog")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        model_box = QGroupBox("Model downloads")
        model_layout = QVBoxLayout(model_box)
        model_layout.setContentsMargins(16, 20, 16, 14)
        model_layout.setSpacing(10)

        self.model_settings_list = QListWidget()
        self.model_settings_list.setMinimumHeight(86)
        self.model_settings_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.model_settings_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.model_settings_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.model_settings_list.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.model_settings_list.setWordWrap(False)
        self.model_settings_list.setToolTip("Installed and bundled models available for transcription.")
        model_layout.addWidget(self.model_settings_list)

        downloads_widget = QWidget()
        dl_grid = QGridLayout(downloads_widget)
        dl_grid.setContentsMargins(0, 0, 0, 0)
        dl_grid.setHorizontalSpacing(8)
        dl_grid.setVerticalSpacing(8)

        self.download_base_btn = QPushButton("Base")
        self.download_base_btn.setProperty("role", "secondary")
        self.download_base_btn.clicked.connect(lambda: self.download_model("base"))
        self.download_base_btn.setToolTip("Download the small base model for faster transcription.")
        dl_grid.addWidget(self.download_base_btn, 0, 0)

        self.download_small_btn = QPushButton("Small")
        self.download_small_btn.setProperty("role", "secondary")
        self.download_small_btn.clicked.connect(lambda: self.download_model("small"))
        self.download_small_btn.setToolTip("Download the small multilingual model.")
        dl_grid.addWidget(self.download_small_btn, 0, 1)

        self.download_medium_btn = QPushButton("Medium")
        self.download_medium_btn.setProperty("role", "secondary")
        self.download_medium_btn.clicked.connect(lambda: self.download_model("medium"))
        self.download_medium_btn.setToolTip("Download the medium multilingual model.")
        dl_grid.addWidget(self.download_medium_btn, 1, 0)

        self.download_large_btn = QPushButton("Turbo")
        self.download_large_btn.setProperty("role", "secondary")
        self.download_large_btn.clicked.connect(lambda: self.download_model("large-v3-turbo-q5_0"))
        self.download_large_btn.setToolTip("Download the large turbo quantized model.")
        dl_grid.addWidget(self.download_large_btn, 1, 1)

        self.download_buttons = [
            self.download_base_btn,
            self.download_small_btn,
            self.download_medium_btn,
            self.download_large_btn,
        ]
        for button in self.download_buttons:
            button.setObjectName("downloadModelButton")
            button.setMinimumWidth(DESIGN_TOKENS["control"]["model_download_min_width"])
        self._sync_button_cursors()

        model_layout.addWidget(downloads_widget)

        self.model_download_progress = QProgressBar()
        self.model_download_progress.setRange(0, 1)
        self.model_download_progress.setValue(0)
        self.model_download_progress.setFormat("")
        self.model_download_progress.setTextVisible(True)
        self.model_download_progress.setToolTip("Shows the current model download progress.")
        model_layout.addWidget(self.model_download_progress)

        self.model_download_status_label = QLabel("Ready")
        self.model_download_status_label.setObjectName("modelDownloadStatus")
        self.model_download_status_label.setWordWrap(True)
        self.model_download_status_label.setToolTip("Current model download status.")
        model_layout.addWidget(self.model_download_status_label)

        layout.addWidget(model_box)

        close_btn = QPushButton("Close")
        close_btn.setProperty("role", "secondary")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.model_settings_dialog = dialog
        self._apply_theme()
        return dialog

    def refresh_model_settings_list(self) -> None:
        if self.model_settings_list is None:
            return

        self.model_settings_list.clear()
        items = self.model_manager.available_models()
        if not items:
            item = QListWidgetItem("No model installed")
            item.setToolTip("No model installed")
            self.model_settings_list.addItem(item)
            return

        for key, path, source in items:
            display = MODEL_DEFS.get(key).label if key in MODEL_DEFS else key
            text = f"{display} - {source} - {path.name}"
            item = QListWidgetItem(text)
            item.setToolTip(text)
            self.model_settings_list.addItem(item)

    def set_model_download_status(self, text: str, percent: int | None = 0) -> None:
        if self.model_download_status_label is not None:
            self.model_download_status_label.setText(text)

        if self.model_download_progress is None:
            return

        if percent is None:
            self.model_download_progress.setRange(0, 0)
            self.model_download_progress.setFormat("")
            return

        value = max(0, min(100, percent))
        self.model_download_progress.setRange(0, 100)
        self.model_download_progress.setValue(value)
        self.model_download_progress.setFormat("Done" if value == 100 else f"{value}%")

    def ensure_default_model_available(self, force: bool = False) -> None:
        if self.current_model_key() is not None or self.current_worker is not None:
            return
        if self.auto_model_prompted and not force:
            return

        self.auto_model_prompted = True
        self.progress_label.setText("Download a model from Settings before transcribing.")
        action = self._prompt_model_download()
        if action == "download":
            self.show_model_settings()
            self.download_model(DEFAULT_DOWNLOAD_MODEL_KEY)
            return
        if action == "settings":
            self.show_model_settings()

    def _prompt_model_download(self) -> str:
        model = self.model_manager.default_download_model()
        prompt = QMessageBox(self)
        prompt.setIcon(QMessageBox.Icon.Question)
        prompt.setWindowTitle("Model required")
        prompt.setText("No transcription model is installed.")
        prompt.setInformativeText(
            f"Download {model.label} ({model.size_label}) now, "
            "or choose a different model in Settings."
        )
        download_button = prompt.addButton(
            f"Download {model.label}",
            QMessageBox.ButtonRole.AcceptRole,
        )
        settings_button = prompt.addButton(
            "Choose model...",
            QMessageBox.ButtonRole.ActionRole,
        )
        prompt.addButton(QMessageBox.StandardButton.Cancel)
        prompt.setDefaultButton(download_button)
        prompt.exec()

        clicked = prompt.clickedButton()
        if clicked == download_button:
            return "download"
        if clicked == settings_button:
            return "settings"
        return "cancel"

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

        model_key = self.current_model_key()
        if model_key is None:
            self.ensure_default_model_available(force=True)
            return

        try:
            model_file = self.model_manager.resolve_model_path(model_key)
        except Exception as exc:
            QMessageBox.critical(self, "Model error", str(exc))
            return

        output_dir = self._choose_output_dir("Select output folder")
        if not output_dir:
            return

        self.progress_label.setText("Preparing transcription...")

        # Make sure the file is represented in the queue and mark it running, so it
        # stays visible and gets a ✓ when finished instead of disappearing.
        self.current_single_index = self._ensure_queue_index(self.selected_file)
        item = self.batch_items[self.current_single_index]
        item["status"] = "running"
        item["error"] = None
        self.refresh_batch_list()
        self._select_queue_row(self.current_single_index)

        opts = TranscriptionOptions(
            input_file=self.selected_file,
            model_file=model_file,
            language=self.source_language_combo.currentData() or "auto",
            output_format=self.output_combo.currentText(),
            target_language=self.target_language_combo.currentData() or "as_source",
            save_timestamps=self.save_timestamps_checkbox.isChecked(),
            output_dir=output_dir,
        )
        self.progress.setRange(0, 0)
        self.progress.setFormat("")
        self.append_log("Starting transcription...")
        worker = TranscribeWorker(opts)
        worker.signals.log.connect(self.append_log)
        worker.signals.error.connect(self.on_worker_error)
        worker.signals.finished.connect(self.on_transcription_finished)
        worker.signals.cancelled.connect(self.on_transcription_cancelled)
        self.current_worker = worker
        self.current_mode = "single"
        self.sync_action_controls()
        self.thread_pool.start(worker)

    def _ensure_queue_index(self, path: Path) -> int:
        target = str(path)
        for index, item in enumerate(self.batch_items):
            if str(item["path"]) == target:
                return index
        self.batch_items.append({"path": Path(path), "status": "queued", "output": None, "error": None})
        return len(self.batch_items) - 1

    def on_transcription_finished(self, output_path) -> None:
        output_path = Path(output_path)
        if self.current_single_index is not None and 0 <= self.current_single_index < len(self.batch_items):
            item = self.batch_items[self.current_single_index]
            item["status"] = "done"
            item["output"] = output_path
            item["error"] = None
            self.refresh_batch_list()
        self.current_single_index = None
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.progress.setFormat("Done")
        self.progress_label.setText("Transcription complete")
        self.append_log(f"Done: {output_path}")
        self.load_transcript(output_path)
        QMessageBox.information(self, "Completed", f"Output saved to:\n{output_path}")
        self.current_worker = None
        self.current_mode = None
        self.sync_action_controls()

    def on_worker_error(self, message: str) -> None:
        if self.current_single_index is not None and 0 <= self.current_single_index < len(self.batch_items):
            item = self.batch_items[self.current_single_index]
            item["status"] = "failed"
            item["error"] = message
            self.refresh_batch_list()
        self.current_single_index = None
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress.setFormat("%p%")
        self.progress_label.setText("Stopped")
        self.append_log(f"ERROR: {message}")
        QMessageBox.critical(self, "Error", message)
        self.current_worker = None
        self.current_mode = None
        self.sync_action_controls()

    def _choose_output_dir(self, caption: str) -> str:
        # Use the native macOS panel: it conforms to the system look, and it is
        # the only chooser that lists cloud / File-Provider folders (e.g. kDrive,
        # OneDrive) — Qt's own dialog cannot enumerate those. Pass empty options
        # (i.e. NOT ShowDirsOnly): on recent macOS, ShowDirsOnly greys out folders
        # so nothing can be selected. Without it, files show greyed and folders
        # stay selectable. The last folder is remembered between runs.
        start_dir = str(self.settings.value("output/last_dir", "") or Path.home())
        output_dir = QFileDialog.getExistingDirectory(
            self,
            caption,
            start_dir,
            QFileDialog.Option(0),
        )
        if output_dir:
            self.settings.setValue("output/last_dir", output_dir)
        return output_dir

    def open_outputs(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(outputs_dir())))

    def load_media(self, path: Path) -> None:
        self.media_player.stop()
        self.media_player.setSource(QUrl.fromLocalFile(str(path)))
        self.media_slider.setValue(0)
        self.media_loaded = True
        self.play_pause_btn.setText("Play")
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.position_label.setText("00:00")
        self.duration_label.setText("00:00")
        self.sync_action_controls()

    def toggle_playback(self) -> None:
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            return
        self.media_player.play()

    def stop_media(self) -> None:
        self.media_player.stop()
        self.media_slider.setValue(0)

    def seek_media(self, position: int) -> None:
        self.media_player.setPosition(position)

    def on_media_duration_changed(self, duration: int) -> None:
        self.media_slider.setRange(0, max(0, duration))
        self.duration_label.setText(_format_milliseconds(duration))

    def on_media_position_changed(self, position: int) -> None:
        if not self.media_slider.isSliderDown():
            self.media_slider.setValue(position)
        self.position_label.setText(_format_milliseconds(position))

    def on_playback_state_changed(self, state) -> None:
        is_playing = state == QMediaPlayer.PlaybackState.PlayingState
        self.play_pause_btn.setText("Pause" if is_playing else "Play")
        icon = QStyle.StandardPixmap.SP_MediaPause if is_playing else QStyle.StandardPixmap.SP_MediaPlay
        self.play_pause_btn.setIcon(self.style().standardIcon(icon))
        self.sync_action_controls()

    def on_media_error(self, error, message: str) -> None:
        if error == QMediaPlayer.Error.NoError:
            return
        self.append_log(f"MEDIA ERROR: {message or error}")

    def open_transcript_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open transcript",
            str(outputs_dir()),
            "Transcript files (*.txt *.srt *.vtt);;All files (*.*)",
        )
        if file_path:
            self.load_transcript(Path(file_path))

    def load_transcript(self, path: Path) -> None:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text()
        except Exception as exc:
            QMessageBox.critical(self, "Transcript error", f"Could not open transcript:\n{exc}")
            return

        self.current_transcript_path = path
        self.transcript_editor.setPlainText(text)
        self.transcript_editor.setEnabled(True)
        self.transcript_label.setText(str(path))
        self.append_log(f"Transcript loaded: {path}")
        self.sync_action_controls()

    def save_transcript(self) -> None:
        if not self.current_transcript_path:
            QMessageBox.warning(self, "Missing transcript", "Open a transcript before saving.")
            return

        confirmation = QMessageBox(self)
        confirmation.setIcon(QMessageBox.Icon.Warning)
        confirmation.setWindowTitle("Overwrite transcript?")
        confirmation.setText("Save changes will overwrite the existing transcript file.")
        confirmation.setInformativeText(
            f"{self.current_transcript_path}\n\nDo you want to continue?"
        )
        overwrite_button = confirmation.addButton(
            "Overwrite",
            QMessageBox.ButtonRole.AcceptRole,
        )
        confirmation.addButton(QMessageBox.StandardButton.Cancel)
        confirmation.setDefaultButton(QMessageBox.StandardButton.Cancel)
        confirmation.exec()

        if confirmation.clickedButton() != overwrite_button:
            self.append_log("Transcript save cancelled.")
            return

        try:
            self.current_transcript_path.write_text(self.transcript_editor.toPlainText(), encoding="utf-8")
        except Exception as exc:
            QMessageBox.critical(self, "Save error", f"Could not save transcript:\n{exc}")
            return

        self.append_log(f"Transcript saved: {self.current_transcript_path}")
        self.progress_label.setText(f"Saved transcript: {self.current_transcript_path.name}")

    def download_model(self, model_key: str) -> None:
        model = MODEL_DEFS.get(model_key)
        label = model.label if model else model_key
        self.set_model_download_status(f"Preparing download: {label}", 0)
        self.download_started_at = time.monotonic()
        self.active_download_model_key = model_key
        worker = DownloadModelWorker(model_key, self.model_manager)
        worker.signals.progress.connect(self.on_download_progress)
        worker.signals.error.connect(self.on_download_error)
        worker.signals.finished.connect(self.on_download_finished)
        self.current_worker = worker
        self.current_mode = "download"
        self.sync_action_controls()
        self.thread_pool.start(worker)

    def on_download_progress(self, done: int, total: int) -> None:
        label = self.active_download_model_key or "model"
        if label in MODEL_DEFS:
            label = MODEL_DEFS[label].label
        elapsed = max(time.monotonic() - self.download_started_at, 0.001)
        speed = done / elapsed

        if total <= 0:
            self.set_model_download_status(
                f"Downloading {label}: {_format_bytes(done)} downloaded at {_format_bytes(speed)}/s",
                None,
            )
            return

        percent = max(0, min(100, int(done * 100 / total)))
        self.set_model_download_status(
            f"Downloading {label}: {_format_bytes(done)} / {_format_bytes(total)} at {_format_bytes(speed)}/s",
            percent,
        )

    def on_download_finished(self, path) -> None:
        self.set_model_download_status(f"Download complete: {Path(path).name}", 100)
        self.refresh_models()
        self.current_worker = None
        self.current_mode = None
        self.active_download_model_key = None
        self.sync_action_controls()

    def on_download_error(self, message: str) -> None:
        self.set_model_download_status(f"Download failed: {message}", 0)
        QMessageBox.critical(self, "Download error", message)
        self.current_worker = None
        self.current_mode = None
        self.active_download_model_key = None
        self.sync_action_controls()

    def stop_transcription(self):
        if self.current_mode not in {"single", "batch"}:
            return
        self.append_log("Stop requested by user...")
        worker = getattr(self, "current_worker", None)
        if worker is not None:
            try:
                worker.cancel()
            except Exception as exc:
                self.append_log(f"Stop failed: {exc}")

    def on_transcription_cancelled(self):
        self.append_log("Transcription cancelled.")
        if self.current_single_index is not None and 0 <= self.current_single_index < len(self.batch_items):
            # Return the file to the queue so it can be retried.
            self.batch_items[self.current_single_index]["status"] = "queued"
            self.refresh_batch_list()
        self.current_single_index = None
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress_label.setText("Cancelled")
        self.current_worker = None
        self.current_mode = None
        self.sync_action_controls()

    def check_engine_updates(self, manual: bool = False) -> None:
        if self.current_worker is not None:
            if manual:
                QMessageBox.information(
                    self,
                    "Please wait",
                    "Another operation is in progress. Try again when it finishes.",
                )
            return
        if not manual and self.engine_update_prompted:
            return
        self.append_log("Checking for Whisper engine updates...")
        worker = EngineUpdateCheckWorker()
        worker.signals.log.connect(self.append_log)
        worker.signals.finished.connect(lambda info: self.on_engine_check_finished(info, manual))
        self._engine_check_worker = worker
        self.thread_pool.start(worker)

    def on_engine_check_finished(self, info, manual: bool) -> None:
        self.engine_update_prompted = True
        self._engine_check_worker = None
        if not info:
            self.append_log(
                f"Whisper engine is up to date ({engine_manager.installed_engine_version()})."
            )
            if manual:
                QMessageBox.information(
                    self,
                    "Whisper engine",
                    f"You already have the latest engine ({engine_manager.installed_engine_version()}).",
                )
            return
        self.append_log(f"Whisper engine update available: {info.get('version')}")
        if self.current_worker is not None:
            self.append_log("Engine update available, but skipped because the app is busy.")
            return
        self.prompt_engine_update(info)

    def prompt_engine_update(self, info: dict) -> None:
        version = info.get("version", "?")
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Question)
        box.setWindowTitle("Whisper engine update")
        box.setText(f"A new Whisper engine ({version}) is available.")
        box.setInformativeText(
            "Updating will download the required components and replace the engine "
            "used for transcription. Your models and transcripts are not affected.\n\n"
            "Update now?"
        )
        update_btn = box.addButton("Update now", QMessageBox.ButtonRole.AcceptRole)
        box.addButton("Later", QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(update_btn)
        box.exec()
        if box.clickedButton() is update_btn:
            self.start_engine_update(info)
        else:
            self.append_log("Engine update postponed by user.")

    def start_engine_update(self, info: dict) -> None:
        version = info.get("version", "?")
        worker = EngineUpdateWorker(info)
        worker.signals.log.connect(self.append_log)
        worker.signals.progress.connect(self.on_engine_update_progress)
        worker.signals.finished.connect(self.on_engine_update_finished)
        worker.signals.error.connect(self.on_engine_update_error)
        self.current_worker = worker
        self.current_mode = "engine"
        self.progress.setRange(0, 0)
        self.progress.setFormat("")
        self.progress_label.setText(f"Downloading Whisper engine {version}...")
        self.append_log(f"Downloading Whisper engine {version}...")
        self.sync_action_controls()
        self.thread_pool.start(worker)

    def on_engine_update_progress(self, done: int, total: int) -> None:
        if total > 0:
            self.progress.setRange(0, total)
            self.progress.setValue(done)
            self.progress.setFormat("%p%")
            self.progress_label.setText(
                f"Downloading Whisper engine: {_format_bytes(done)} / {_format_bytes(total)}"
            )
        else:
            self.progress.setRange(0, 0)

    def on_engine_update_finished(self, version) -> None:
        self.current_worker = None
        self.current_mode = None
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.progress.setFormat("Done")
        self.progress_label.setText(f"Whisper engine updated to {version}")
        self.append_log(f"Whisper engine updated to {version}")
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Information)
        box.setWindowTitle("Engine updated")
        box.setText(f"Whisper engine updated to {version}.")
        box.setInformativeText(
            "It will be used for the next transcription.\n\n"
            "If macOS blocks the new engine, see the security steps."
        )
        security_btn = box.addButton("macOS security & permissions", QMessageBox.ButtonRole.ActionRole)
        box.addButton(QMessageBox.StandardButton.Ok)
        box.exec()
        if box.clickedButton() is security_btn:
            self.show_security_help()
        self.sync_action_controls()

    def on_engine_update_error(self, message: str) -> None:
        self.current_worker = None
        self.current_mode = None
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress.setFormat("%p%")
        self.progress_label.setText("Engine update failed")
        self.append_log(f"ENGINE UPDATE ERROR: {message}")
        QMessageBox.critical(self, "Engine update failed", message)
        self.sync_action_controls()

    def check_model_updates(self, manual: bool = False) -> None:
        if self.current_worker is not None:
            if manual:
                QMessageBox.information(
                    self,
                    "Please wait",
                    "Another operation is in progress. Try again when it finishes.",
                )
            return
        if not manual and self.model_update_prompted:
            return
        self.append_log("Checking for model updates...")
        worker = ModelUpdateCheckWorker(self.model_manager)
        worker.signals.log.connect(self.append_log)
        worker.signals.finished.connect(lambda updates: self.on_model_check_finished(updates, manual))
        self._model_check_worker = worker
        self.thread_pool.start(worker)

    def on_model_check_finished(self, updates, manual: bool) -> None:
        self.model_update_prompted = True
        self._model_check_worker = None
        if not updates:
            self.append_log("Models are up to date.")
            if manual:
                QMessageBox.information(self, "Models", "Your installed models are up to date.")
            return
        self.append_log("Model update available: " + ", ".join(m.label for m in updates))
        if self.current_worker is not None:
            self.append_log("Model update available, but skipped because the app is busy.")
            return
        self.prompt_model_update(updates)

    def prompt_model_update(self, updates: list) -> None:
        names = ", ".join(m.label for m in updates)
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Question)
        box.setWindowTitle("Model update")
        box.setText(f"An updated version is available for: {names}.")
        box.setInformativeText(
            "Updating re-downloads the model file(s) and verifies them by checksum. "
            "This can be a large download.\n\nUpdate now?"
        )
        update_btn = box.addButton("Update now", QMessageBox.ButtonRole.AcceptRole)
        box.addButton("Later", QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(update_btn)
        box.exec()
        if box.clickedButton() is update_btn:
            self.start_model_update(updates)
        else:
            self.append_log("Model update postponed by user.")

    def start_model_update(self, updates: list) -> None:
        worker = ModelUpdateWorker(self.model_manager, updates)
        worker.signals.log.connect(self.append_log)
        worker.signals.progress.connect(self.on_model_update_progress)
        worker.signals.finished.connect(self.on_model_update_finished)
        worker.signals.error.connect(self.on_model_update_error)
        self.current_worker = worker
        self.current_mode = "modeldl"
        self.progress.setRange(0, 0)
        self.progress.setFormat("")
        self.progress_label.setText("Updating model(s)...")
        self.append_log("Updating model(s)...")
        self.sync_action_controls()
        self.thread_pool.start(worker)

    def on_model_update_progress(self, done: int, total: int) -> None:
        if total > 0:
            self.progress.setRange(0, total)
            self.progress.setValue(done)
            self.progress.setFormat("%p%")
            self.progress_label.setText(
                f"Updating model: {_format_bytes(done)} / {_format_bytes(total)}"
            )
        else:
            self.progress.setRange(0, 0)

    def on_model_update_finished(self, keys) -> None:
        self.current_worker = None
        self.current_mode = None
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.progress.setFormat("Done")
        self.progress_label.setText("Model(s) updated")
        self.append_log(f"Model(s) updated: {', '.join(keys)}")
        self.refresh_models()
        QMessageBox.information(self, "Models updated", "The selected model(s) were updated.")
        self.sync_action_controls()

    def on_model_update_error(self, message: str) -> None:
        self.current_worker = None
        self.current_mode = None
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress.setFormat("%p%")
        self.progress_label.setText("Model update failed")
        self.append_log(f"MODEL UPDATE ERROR: {message}")
        QMessageBox.critical(self, "Model update failed", message)
        self.sync_action_controls()

    def show_security_help(self) -> None:
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Information)
        box.setWindowTitle("macOS security & permissions")
        box.setText("Allowing Transcriber-LP and its Whisper engine on macOS")
        box.setInformativeText(
            "Usually you don't need to change anything — the app and the "
            "downloaded engine run without prompts. These steps are only for the "
            "rare cases below.\n\n"
            "If macOS blocks the app or the downloaded Whisper engine "
            '("cannot be opened because the developer cannot be verified"), '
            "allow it once:\n\n"
            "1. Open the Apple menu  > System Settings.\n"
            "2. Go to Privacy & Security.\n"
            "3. Scroll down to the Security section.\n"
            "4. Next to the message about Transcriber-LP (or \"whisper-cli\") being "
            "blocked, click \"Open Anyway\".\n"
            "5. Confirm with \"Open\" and your password or Touch ID if asked.\n\n"
            "To read or write files in protected locations (Desktop, Documents, "
            "Downloads, iCloud or kDrive):\n"
            "1. System Settings > Privacy & Security > Files and Folders "
            "(or Full Disk Access).\n"
            "2. Enable access for Transcriber-LP.\n\n"
            "Use the button below to jump straight to Privacy & Security."
        )
        open_btn = box.addButton("Open Privacy & Security", QMessageBox.ButtonRole.ActionRole)
        box.addButton(QMessageBox.StandardButton.Close)
        box.exec()
        if box.clickedButton() is open_btn:
            QDesktopServices.openUrl(
                QUrl("x-apple.systempreferences:com.apple.settings.PrivacySecurity.extension")
            )

    def show_help(self) -> None:
        manual = (
            "Transcriber-LP Manual:\n\n"
            "1) Aggiungi uno o piu file audio/video con 'Add or Drop files here' o trascinandoli nella finestra: ogni file entra nella Queue. I file trascinati insieme vengono aggiunti dal piu vecchio al piu nuovo per data.\n"
            "2) Scegli il formato di uscita: txt, srt o vtt.\n"
            "3) Controlla Current Model. Se non c'e un modello, l'app propone il download o apre Settings.\n"
            "4) Opzionalmente imposta la lingua sorgente o lascia Auto-detect per la rilevazione automatica.\n"
            "5) Scegli se mantenere la lingua originale o tradurre in inglese.\n"
            "6) Abilita Timestamped output se vuoi timecode nel TXT e un CSV con i timestamp.\n"
            "7) Clicca Transcribe selected per trascrivere solo il file selezionato nella coda; usa Stop per annullare la trascrizione in corso.\n"
            "8) Usa Reset per azzerare coda, anteprima, editor e progresso e iniziare una nuova sessione: gli output gia salvati su disco non vengono toccati.\n\n"
            "Queue:\n"
            "- La coda e una tabella con le colonne File, Date e Status: clicca un'intestazione per ordinare la coda (di nuovo per invertire). L'ordinamento e disattivato durante una trascrizione.\n"
            "- Riordina manualmente la coda trascinando le righe, con i pulsanti freccia su/giu accanto a Remove, o dal menu contestuale (Sposta su / Sposta giu). Il riordino manuale sostituisce l'ordinamento per colonna ed e disattivato durante una trascrizione.\n"
            "- I file restano nella coda: ▶ in corso, ✓ completato, ✗ fallito. Non spariscono dopo la trascrizione.\n"
            "- Usa Transcribe queue per trascrivere in sequenza tutti i file non ancora completati nello stesso output folder.\n"
            "- La barra mostra l'avanzamento (X/Y) e quali file sono stati fatti.\n"
            "- Le icone in basso a destra: ✓ rimuove i completati (Clear done), il cestino svuota tutta la coda (Clear all).\n"
            "- Retrieve output (o doppio click) riapre un output completato nell'editor.\n\n"
            "Review:\n"
            "- Il file sorgente selezionato viene caricato nel player di anteprima.\n"
            "- Quando la trascrizione finisce, il file generato si apre nel Transcript Editor.\n"
            "- Correggi il testo e usa Save changes per salvare sullo stesso file dopo conferma.\n"
            "- Usa Open transcript per aprire una trascrizione esistente.\n\n"
            "Appearance:\n"
            "- Usa View > Theme per passare tra tema chiaro e tema scuro.\n"
            "- La scelta del tema viene ricordata al prossimo avvio.\n\n"
            "Note:\n"
            "- Le trascrizioni vengono salvate in ~/Library/Application Support/Transcriber-LP/outputs.\n"
            "- I modelli scaricati vengono memorizzati in ~/Library/Application Support/Transcriber-LP/models.\n"
            "- Se non è presente nessun modello, l'app propone un download verificato e Current Model apre Settings.\n"
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
                "Offline desktop transcription and review app for macOS.\n"
                "Versioning follows semantic versioning from the first tracked public-ready baseline."
            ),
        )

    def _settings_bool(self, key: str, default: bool) -> bool:
        value = self.settings.value(key, default)
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() not in {"0", "false", "no", "off"}

    def _configure_combo(self, combo: QComboBox) -> None:
        control = DESIGN_TOKENS["control"]
        combo.setCursor(Qt.CursorShape.PointingHandCursor)
        combo.setMinimumHeight(control["min_height"])
        combo.setMinimumWidth(control["combo_min_width"])
        combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        combo.setMaxVisibleItems(10)
        combo.setFrame(False)
        combo.view().setCursor(Qt.CursorShape.PointingHandCursor)
        combo.view().setMouseTracking(True)
        combo.view().viewport().setMouseTracking(True)
        combo.view().viewport().setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        combo.view().setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        combo.view().setFrameShape(QFrame.Shape.NoFrame)
        combo.view().setLineWidth(0)
        combo.view().setMidLineWidth(0)
        combo.view().setUniformItemSizes(True)
        combo.view().setMinimumWidth(control["combo_min_width"])
        combo.view().entered.connect(combo.view().setCurrentIndex)
        hover_filter = ComboPopupHoverFilter(combo.view())
        combo.view().viewport().installEventFilter(hover_filter)
        combo._transcriber_hover_filter = hover_filter
        combo.view().setItemDelegate(ComboItemDelegate(combo.view()))
        if combo not in getattr(self, "styled_combos", []):
            self.styled_combos.append(combo)
        if hasattr(combo.view(), "setSpacing"):
            combo.view().setSpacing(2)

    def _set_download_controls_enabled(self, enabled: bool) -> None:
        for button in getattr(self, "download_buttons", []):
            button.setEnabled(enabled)

    def _sync_button_cursors(self) -> None:
        for button in self.findChildren(QPushButton):
            cursor = Qt.CursorShape.PointingHandCursor if button.isEnabled() else Qt.CursorShape.ArrowCursor
            button.setCursor(cursor)

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

    def _sync_combo_item_delegates(self, colors: dict[str, str]) -> None:
        for combo in getattr(self, "styled_combos", []):
            combo.setProperty("chevronColor", colors["arrow"])
            combo.update()
            delegate = combo.view().itemDelegate()
            if isinstance(delegate, ComboItemDelegate):
                delegate.set_colors(
                    hover_bg=colors["list_hover_bg"],
                    hover_text=colors["list_hover_text"],
                    text=colors["input_text"],
                )
                combo.view().viewport().update()
            popup_delegate = getattr(combo, "_popup_delegate", None)
            if isinstance(popup_delegate, ComboPopupListDelegate):
                popup_delegate.set_colors(
                    hover_bg=colors["list_hover_bg"],
                    hover_text=colors["list_hover_text"],
                    text=colors["input_text"],
                    check=colors["arrow"],
                )
                if getattr(combo, "_popup_list", None) is not None:
                    combo._popup_list.viewport().update()

    def _apply_theme(self) -> None:
        c = THEME_PALETTES[self.theme_name]
        radius = DESIGN_TOKENS["radius"]
        control = DESIGN_TOKENS["control"]
        self._sync_combo_item_delegates(c)

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
                                f"border-radius: {radius['menu']}px;",
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
                    block(
                        "QLabel#progressLabel,\nQLabel#modelDownloadStatus",
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
                        "QLabel#dropOverlay",
                        "\n".join(
                            [
                                f"color: {c['drop_text']};",
                                f"background: {_hex_to_rgba(c['drop_hover_bg'], 0.93)};",
                                f"border: 3px dashed {c['drop_hover_border']};",
                                "border-radius: 16px;",
                                "padding: 18px;",
                                "font-size: 22px;",
                                "font-weight: 800;",
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
                    block(
                        'QLabel[role="settingsLabel"]',
                        "\n".join(
                            [
                                f"color: {c['field_label']};",
                                "font-weight: 700;",
                            ]
                        ),
                    ),
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
                        "QPushButton:enabled:hover",
                        f"background: {c['button_hover_bg']};\nborder-color: {c['button_hover_border']};",
                    ),
                    block("QPushButton:enabled:pressed", f"background: {c['button_pressed_bg']};"),
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
                        'QPushButton[role="primary"]:enabled:hover',
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
                        'QPushButton[role="danger"]:enabled:hover',
                        f"background: {c['danger_hover_bg']};\nborder-color: {c['danger_hover_bg']};",
                    ),
                    block(
                        'QPushButton[role="secondary"]',
                        f"background: {c['secondary_bg']};\nborder-color: {c['secondary_border']};",
                    ),
                    block(
                        'QPushButton[role="secondary"]:enabled:hover',
                        "\n".join(
                            [
                                f"background: {c['button_hover_bg']};",
                                f"border-color: {c['button_hover_border']};",
                                f"color: {c['button_text']};",
                            ]
                        ),
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
                        "QPushButton#browseButton:enabled:hover",
                        "\n".join(
                            [
                                f"background: {c['primary_bg']};",
                                f"border-color: {c['primary_hover_bg']};",
                                f"color: {c['primary_text']};",
                            ]
                        ),
                    ),
                    block("QPushButton#browseButton:enabled:pressed", f"background: {c['primary_hover_bg']};"),
                    block(
                        "QPushButton#downloadModelButton",
                        "\n".join(
                            [
                                "min-height: 32px;",
                                "padding: 6px 10px;",
                            ]
                        ),
                    ),
                    block(
                        "QPushButton#iconButton",
                        "\n".join(
                            [
                                "min-height: 32px;",
                                "padding: 4px;",
                            ]
                        ),
                    ),
                    block(
                        "QPushButton:disabled,\n"
                        'QPushButton[role="primary"]:disabled,\n'
                        'QPushButton[role="danger"]:disabled,\n'
                        'QPushButton[role="secondary"]:disabled,\n'
                        "QPushButton#browseButton:disabled,\n"
                        "QPushButton#downloadModelButton:disabled",
                        "\n".join(
                            [
                                f"color: {c['button_disabled_text']};",
                                f"background: {c['button_disabled_bg']};",
                                f"border-color: {c['button_disabled_border']};",
                            ]
                        ),
                    ),
                    block(
                        "QComboBox",
                        "\n".join(
                            [
                                f"min-height: {control['min_height']}px;",
                                f"color: {c['input_text']};",
                                f"background: {c['input_bg']};",
                                f"border: 1px solid {c['input_border']};",
                                f"border-radius: {radius['control']}px;",
                                (
                                    f"padding: 6px {control['combo_arrow_width']}px "
                                    f"6px {control['horizontal_padding']}px;"
                                ),
                                "font-weight: 600;",
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
                    block("QComboBox::drop-down", f"width: {control['combo_arrow_width']}px;\nborder: none;"),
                    block(
                        "QComboBox::down-arrow",
                        "\n".join(
                            [
                                "image: none;",
                                "width: 0;",
                                "height: 0;",
                                "margin-right: 12px;",
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
                                "border: none;",
                                f"border-radius: {radius['menu']}px;",
                                "outline: 0;",
                                f"padding: {control['combo_popup_padding']}px;",
                            ]
                        ),
                    ),
                    block(
                        "QComboBox QAbstractItemView::item",
                        (
                            f"min-height: {control['combo_popup_item_height']}px;\n"
                            f"padding: 7px {control['horizontal_padding']}px;\n"
                            "border-radius: 6px;"
                        ),
                    ),
                    block(
                        "QComboBox QAbstractItemView::item:hover",
                        f"background: {c['list_hover_bg']};\ncolor: {c['list_hover_text']};",
                    ),
                    block(
                        "QComboBox QAbstractItemView::item:selected",
                        f"background: {c['list_hover_bg']};\ncolor: {c['list_hover_text']};",
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
                        "QListWidget,\nQTableWidget,\nQPlainTextEdit",
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
                        "QTableWidget#queueTable",
                        f"gridline-color: transparent;\nbackground: {c['list_bg']};",
                    ),
                    block(
                        "QTableWidget::item",
                        "padding: 4px 6px;\nborder: none;",
                    ),
                    block(
                        "QTableWidget::item:selected",
                        f"background: {c['selection_bg']};\ncolor: {c['selection_text']};",
                    ),
                    block(
                        "QHeaderView::section",
                        "\n".join(
                            [
                                f"color: {c['field_label']};",
                                f"background: {c['group_title_bg']};",
                                "border: none;",
                                f"border-bottom: 1px solid {c['list_border']};",
                                "padding: 5px 8px;",
                                "font-weight: 700;",
                            ]
                        ),
                    ),
                    block(
                        "QHeaderView::section:hover",
                        f"color: {c['list_hover_text']};\nbackground: {c['list_hover_bg']};",
                    ),
                    block(
                        "QTableCornerButton::section",
                        f"background: {c['group_title_bg']};\nborder: none;",
                    ),
                    block(
                        "QPlainTextEdit#logPanel",
                        'font-family: "Menlo", "Consolas", monospace;\nfont-size: 12px;\nline-height: 1.4;',
                    ),
                    block(
                        "QPlainTextEdit#transcriptEditor",
                        'font-family: "Menlo", "Consolas", monospace;\nfont-size: 13px;\nline-height: 1.5;',
                    ),
                    block(
                        "QVideoWidget#videoPreview",
                        "\n".join(
                            [
                                "background: #050709;",
                                f"border: 1px solid {c['list_border']};",
                                "border-radius: 8px;",
                            ]
                        ),
                    ),
                    block(
                        "QLabel#timeLabel",
                        f"color: {c['status_text']};\nfont-weight: 650;",
                    ),
                    block(
                        "QLabel#transcriptLabel",
                        f"color: {c['status_text']};\nfont-weight: 600;",
                    ),
                    block(
                        "QSlider::groove:horizontal",
                        f"height: 6px;\nbackground: {c['progress_bg']};\nborder-radius: 3px;",
                    ),
                    block(
                        "QSlider::handle:horizontal",
                        f"width: 14px;\nheight: 14px;\nmargin: -5px 0;\nbackground: {c['primary_bg']};\nborder: 1px solid {c['primary_border']};\nborder-radius: 7px;",
                    ),
                    block("QListWidget::item", "border-radius: 7px;\npadding: 5px 7px;\nmargin: 2px;"),
                    block("QListWidget::item:selected", f"background: {c['selection_bg']};"),
                    block(
                        "QDialog#settingsDialog",
                        "\n".join(
                            [
                                f"background: {c['app_bg']};",
                                f"color: {c['root_text']};",
                            ]
                        ),
                    ),
                    block(
                        "QFrame#comboPopupFrame",
                        "\n".join(
                            [
                                f"background: {c['group_bg']};",
                                "border: none;",
                                f"border-radius: {radius['menu']}px;",
                            ]
                        ),
                    ),
                    block(
                        "QListWidget#comboPopupList",
                        "\n".join(
                            [
                                f"color: {c['input_text']};",
                                f"background: {c['group_bg']};",
                                "border: none;",
                                f"border-radius: {radius['menu']}px;",
                                "outline: 0;",
                                f"padding: {control['combo_popup_padding']}px;",
                                f"selection-background-color: {c['list_hover_bg']};",
                                f"selection-color: {c['list_hover_text']};",
                            ]
                        ),
                    ),
                    block(
                        "QListWidget#comboPopupList::item",
                        (
                            f"min-height: {control['combo_popup_item_height']}px;\n"
                            f"padding: 7px {control['horizontal_padding']}px;\n"
                            "border-radius: 6px;\n"
                            "border: none;\n"
                            "outline: 0;\n"
                            "margin: 0;"
                        ),
                    ),
                    block(
                        "QListWidget#comboPopupList::item:hover",
                        f"background: {c['list_hover_bg']};\ncolor: {c['list_hover_text']};",
                    ),
                    block(
                        "QListWidget#comboPopupList::item:selected",
                        "background: transparent;",
                    ),
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


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    value = hex_color.lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    try:
        r, g, b = (int(value[i : i + 2], 16) for i in (0, 2, 4))
    except (ValueError, IndexError):
        return hex_color
    return f"rgba({r}, {g}, {b}, {alpha})"


def _format_bytes(value):
    size = float(value or 0)
    units = ["B", "KiB", "MiB", "GiB"]
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024


def _format_milliseconds(value: int) -> str:
    total_seconds = max(0, int(value / 1000))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def _count_stems(paths: list[Path]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in paths:
        counts[path.stem] = counts.get(path.stem, 0) + 1
    return counts


def _batch_output_name(path: Path, index: int, stem_counts: dict[str, int]) -> str | None:
    if stem_counts.get(path.stem, 0) <= 1:
        return None
    return f"{path.stem}_{index + 1:02d}"
