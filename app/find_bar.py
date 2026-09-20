from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel
)
from PySide6.QtWebEngineCore import QWebEnginePage

from app.browser_view import BrowserView


class FindBar(QWidget):

    closed = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(38)
        self.hide()

        self.setStyleSheet(
            "QWidget { background: rgba(20, 22, 40, 0.95); border-top: 1px solid rgba(255,255,255,0.1); }"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(6)

        self.input = QLineEdit()
        self.input.setFixedHeight(28)
        self.input.setPlaceholderText("Find in page...")
        self.input.setMaximumWidth(280)
        self.input.setStyleSheet(
            "QLineEdit { background: rgba(255,255,255,0.08); color: white;"
            "border: 1px solid rgba(255,255,255,0.15); border-radius: 5px; padding: 2px 8px; }"
            "QLineEdit:focus { border-color: rgba(74, 110, 255, 0.6); }"
        )

        self.result_label = QLabel("")
        self.result_label.setStyleSheet("color: rgba(255,255,255,0.45); font-size: 9pt; min-width: 60px;")

        btn_style = (
            "QPushButton { background: rgba(255,255,255,0.07); color: white; border: none;"
            "border-radius: 5px; padding: 3px 10px; font-size: 9pt; }"
            "QPushButton:hover { background: rgba(255,255,255,0.14); }"
            "QPushButton:pressed { background: rgba(74,110,255,0.4); }"
        )

        self.prev_btn = QPushButton("Prev")
        self.prev_btn.setFixedHeight(26)
        self.prev_btn.setStyleSheet(btn_style)

        self.next_btn = QPushButton("Next")
        self.next_btn.setFixedHeight(26)
        self.next_btn.setStyleSheet(btn_style)

        self.close_btn = QPushButton("X")
        self.close_btn.setFixedSize(26, 26)
        self.close_btn.setStyleSheet(
            "QPushButton { background: transparent; color: rgba(255,255,255,0.5); border: none; font-size: 10pt; }"
            "QPushButton:hover { color: white; background: rgba(255,255,255,0.1); border-radius: 13px; }"
        )

        layout.addWidget(self.input)
        layout.addWidget(self.result_label)
        layout.addWidget(self.prev_btn)
        layout.addWidget(self.next_btn)
        layout.addStretch()
        layout.addWidget(self.close_btn)

        self._view: Optional[BrowserView] = None

        self.input.textChanged.connect(self._on_text_changed)
        self.input.returnPressed.connect(self._find_next)
        self.prev_btn.clicked.connect(self._find_prev)
        self.next_btn.clicked.connect(self._find_next)
        self.close_btn.clicked.connect(self.hide_bar)

    def set_view(self, view: Optional[BrowserView]) -> None:
        self._view = view

    def show_bar(self) -> None:
        self.show()
        self.input.setFocus()
        self.input.selectAll()
        if self._view and self.input.text():
            self._view.findText(self.input.text())

    def hide_bar(self) -> None:
        if self._view:
            self._view.findText("")
        self.result_label.setText("")
        self.hide()
        self.closed.emit()

    def _on_text_changed(self, text: str) -> None:
        if not self._view:
            return
        if text:
            self._view.findText(text, QWebEnginePage.FindFlag(0), self._on_find_result)
        else:
            self._view.findText("")
            self.result_label.setText("")
            self.input.setStyleSheet(
                "QLineEdit { background: rgba(255,255,255,0.08); color: white;"
                "border: 1px solid rgba(255,255,255,0.15); border-radius: 5px; padding: 2px 8px; }"
                "QLineEdit:focus { border-color: rgba(74, 110, 255, 0.6); }"
            )

    def _on_find_result(self, result) -> None:
        text = self.input.text()
        if not text:
            return
        found = result.isValid() if hasattr(result, 'isValid') else bool(result)
        if found:
            self.result_label.setText("Found")
            self.input.setStyleSheet(
                "QLineEdit { background: rgba(255,255,255,0.08); color: white;"
                "border: 1px solid rgba(74,255,140,0.45); border-radius: 5px; padding: 2px 8px; }"
            )
        else:
            self.result_label.setText("Not found")
            self.input.setStyleSheet(
                "QLineEdit { background: rgba(255,80,80,0.12); color: white;"
                "border: 1px solid rgba(255,80,80,0.45); border-radius: 5px; padding: 2px 8px; }"
            )

    def _find_next(self) -> None:
        if self._view:
            self._view.findText(self.input.text())

    def _find_prev(self) -> None:
        if self._view:
            self._view.findText(self.input.text(), QWebEnginePage.FindFlag.FindBackward)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.hide_bar()
        else:
            super().keyPressEvent(event)


__all__ = ["FindBar"]
