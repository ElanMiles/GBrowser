from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QLineEdit
)


class TitleBar(QWidget):

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.parent_window = parent
        self._drag_offset: Optional[object] = None
        self.setFixedHeight(46)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)

        self.icon = QLabel("🌐")
        self.title = QLabel("GBrowser")
        self.title.setFont(QFont("Segoe UI", 10))
        self.title.setStyleSheet("color: white")

        self.back = QPushButton("<-")
        self.fwd = QPushButton("->")
        self.reload = QPushButton("⟳")
        for b in (self.back, self.fwd, self.reload):
            b.setFixedSize(28, 28)
            b.setStyleSheet(
                "color:white;background:rgba(255,255,255,0.06);border-radius:6px;"
            )

        self.new_tab = QPushButton("+")
        self.new_tab.setFixedSize(32, 28)
        self.new_tab.setStyleSheet(
            "color:white;background:rgba(255,255,255,0.06);border-radius:6px;"
        )

        self.settings = QPushButton("⚙")
        self.settings.setFixedSize(28, 28)
        self.settings.setStyleSheet(
            "color:white;background:rgba(255,255,255,0.06);border-radius:6px;"
        )

        self.url = QLineEdit()
        self.url.setFixedHeight(30)
        self.url.setStyleSheet(
            "background:rgba(255,255,255,0.14);color:white;border:none;border-radius:6px;padding-left:8px;"
        )
        self.url.setPlaceholderText("Enter the address and press Enter")

        self.min = QPushButton("–")
        self.max = QPushButton("☐")
        self.close = QPushButton("✕")
        for b in (self.min, self.max, self.close):
            b.setFixedSize(36, 26)
            b.setStyleSheet("color:white;background:transparent;border:none;")

        layout.addWidget(self.icon)
        layout.addWidget(self.title)
        layout.addSpacing(8)
        layout.addWidget(self.back)
        layout.addWidget(self.fwd)
        layout.addWidget(self.reload)
        layout.addWidget(self.new_tab)
        layout.addSpacing(8)
        layout.addWidget(self.settings)
        layout.addSpacing(8)
        layout.addWidget(self.url)
        layout.addWidget(self.min)
        layout.addWidget(self.max)
        layout.addWidget(self.close)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            win = self.parent_window
            if win is not None and win.isMaximized():
                rel_x = event.position().x() / max(1.0, self.width())
                self._drag_offset = ("max", rel_x)
            elif win is not None:
                self._drag_offset = event.globalPosition().toPoint() - win.frameGeometry().topLeft()
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if event.buttons() & Qt.LeftButton and self._drag_offset is not None:
            win = self.parent_window
            if win is None:
                return
            if isinstance(self._drag_offset, tuple):
                rel_x = self._drag_offset[1]
                win.showNormal()
                restored_w = win.width()
                offset = int(restored_w * rel_x)
                self._drag_offset = event.globalPosition().toPoint() - QPoint(offset, 10)
            win.move(event.globalPosition().toPoint() - self._drag_offset)
        return super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        if self.parent_window is not None and hasattr(self.parent_window, "toggle_max_restore"):
            self.parent_window.toggle_max_restore()
        return super().mouseDoubleClickEvent(event)

    def set_title(self, text: str) -> None:
        self.title.setText(text)

    def set_icon(self, text_or_emoji: str) -> None:
        self.icon.setText(text_or_emoji)


__all__ = ["TitleBar"]