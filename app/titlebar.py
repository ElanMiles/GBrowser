from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QProgressBar, QSizePolicy
)


_BTN_STYLE = (
    "QPushButton {{ color:white; background:rgba(255,255,255,0.07); border-radius:6px;"
    "border:none; font-size:{fs}pt; }}"
    "QPushButton:hover {{ background:rgba(255,255,255,0.14); }}"
    "QPushButton:pressed {{ background:rgba(74,110,255,0.45); }}"
    "QPushButton:disabled {{ color:rgba(255,255,255,0.25); }}"
)


def _make_btn(text: str, w: int, h: int, tooltip: str = "", font_size: int = 10) -> QPushButton:
    b = QPushButton(text)
    b.setFixedSize(w, h)
    b.setStyleSheet(_BTN_STYLE.format(fs=font_size))
    if tooltip:
        b.setToolTip(tooltip)
    return b


class TitleBar(QWidget):

    home_clicked = Signal()
    find_clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.parent_window = parent
        self._drag_offset: Optional[object] = None
        self.setFixedHeight(52)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        row_widget = QWidget()
        layout = QHBoxLayout(row_widget)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(6)

        self.icon = QLabel("GB")
        self.icon.setStyleSheet(
            "color:white; font-weight:700; font-size:11pt;"
            "background:rgba(74,110,255,0.7); border-radius:6px; padding:2px 5px;"
        )
        self.title = QLabel("GBrowser")
        self.title.setFont(QFont("Segoe UI", 9))
        self.title.setStyleSheet("color: rgba(255,255,255,0.55);")
        self.title.setMaximumWidth(80)

        self.back = _make_btn("<", 28, 28, "Back (Alt+Left)")
        self.fwd = _make_btn(">", 28, 28, "Forward (Alt+Right)")
        self.reload = _make_btn("R", 28, 28, "Reload (F5)", font_size=9)
        self.home_btn = _make_btn("H", 28, 28, "Home (Ctrl+Home)", font_size=9)

        self.url = QLineEdit()
        self.url.setFixedHeight(30)
        self.url.setStyleSheet(
            "QLineEdit { background:rgba(255,255,255,0.10); color:white; border:1px solid rgba(255,255,255,0.1);"
            "border-radius:6px; padding-left:10px; font-size:9.5pt; }"
            "QLineEdit:focus { background:rgba(255,255,255,0.15); border-color:rgba(74,110,255,0.6); }"
        )
        self.url.setPlaceholderText("Search or enter address...")

        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(38)
        self.zoom_label.setStyleSheet("color:rgba(255,255,255,0.4); font-size:8pt;")
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.find_btn = _make_btn("F", 28, 28, "Find in Page (Ctrl+F)", font_size=9)
        self.settings_btn = _make_btn("S", 28, 28, "Settings", font_size=9)

        self.min_btn = _make_btn("-", 36, 26)
        self.min_btn.setStyleSheet(
            "QPushButton { color:white; background:transparent; border:none; }"
            "QPushButton:hover { background:rgba(255,255,255,0.1); border-radius:4px; }"
        )
        self.max_btn = _make_btn("[]", 36, 26, font_size=8)
        self.max_btn.setStyleSheet(
            "QPushButton { color:white; background:transparent; border:none; }"
            "QPushButton:hover { background:rgba(255,255,255,0.1); border-radius:4px; }"
        )
        self.close_btn = _make_btn("X", 36, 26)
        self.close_btn.setStyleSheet(
            "QPushButton { color:white; background:transparent; border:none; }"
            "QPushButton:hover { background:rgba(200,50,50,0.75); border-radius:4px; }"
        )

        layout.addWidget(self.icon)
        layout.addWidget(self.title)
        layout.addSpacing(4)
        layout.addWidget(self.back)
        layout.addWidget(self.fwd)
        layout.addWidget(self.reload)
        layout.addWidget(self.home_btn)
        layout.addSpacing(4)
        layout.addWidget(self.url, 1)
        layout.addWidget(self.zoom_label)
        layout.addWidget(self.find_btn)
        layout.addWidget(self.settings_btn)
        layout.addSpacing(4)
        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()

        outer.addWidget(row_widget)
        outer.addWidget(self.progress_bar)

        self.home_btn.clicked.connect(self.home_clicked)
        self.find_btn.clicked.connect(self.find_clicked)

    def set_progress(self, value: int) -> None:
        if value <= 0 or value >= 100:
            self.progress_bar.hide()
            self.progress_bar.setValue(0)
        else:
            self.progress_bar.show()
            self.progress_bar.setValue(value)

    def set_secure(self, secure: bool) -> None:
        if secure:
            self.url.setStyleSheet(
                "QLineEdit { background:rgba(255,255,255,0.10); color:white;"
                "border:1px solid rgba(60,200,100,0.35); border-radius:6px; padding-left:10px; font-size:9.5pt; }"
                "QLineEdit:focus { background:rgba(255,255,255,0.15); border-color:rgba(74,110,255,0.6); }"
            )
        else:
            self.url.setStyleSheet(
                "QLineEdit { background:rgba(255,255,255,0.10); color:white;"
                "border:1px solid rgba(255,255,255,0.1); border-radius:6px; padding-left:10px; font-size:9.5pt; }"
                "QLineEdit:focus { background:rgba(255,255,255,0.15); border-color:rgba(74,110,255,0.6); }"
            )

    def set_zoom(self, factor: float) -> None:
        self.zoom_label.setText(f"{int(factor * 100)}%")

    def set_title(self, text: str) -> None:
        display = text[:14] + "..." if len(text) > 14 else text
        self.title.setText(display)
        self.title.setToolTip(text)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            win = self.parent_window
            if win is not None and win.isMaximized():
                rel_x = event.position().x() / max(1.0, self.width())
                self._drag_offset = ("max", rel_x)
            elif win is not None:
                self._drag_offset = event.globalPosition().toPoint() - win.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_offset is not None:
            win = self.parent_window
            if win is None:
                return
            if isinstance(self._drag_offset, tuple):
                rel_x = self._drag_offset[1]
                win.showNormal()
                offset = int(win.width() * rel_x)
                self._drag_offset = event.globalPosition().toPoint() - QPoint(offset, 10)
            win.move(event.globalPosition().toPoint() - self._drag_offset)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._drag_offset = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        if self.parent_window is not None and hasattr(self.parent_window, "toggle_max_restore"):
            self.parent_window.toggle_max_restore()
        super().mouseDoubleClickEvent(event)


__all__ = ["TitleBar"]
