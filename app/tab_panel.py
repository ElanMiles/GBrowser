from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QScrollArea, QSizePolicy
)


class _TabButton(QWidget):

    clicked = Signal(int)
    close_clicked = Signal(int)

    _STYLE_ACTIVE = (
        "QWidget#tab_btn_container { background: rgba(255,255,255,0.10); "
        "border-radius: 6px; border-bottom: 2px solid #4a6eff; }"
    )
    _STYLE_INACTIVE = (
        "QWidget#tab_btn_container { background: transparent; border-radius: 6px; border: none; }"
        "QWidget#tab_btn_container:hover { background: rgba(255,255,255,0.05); }"
    )

    def __init__(self, index: int, title: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.index = index
        self.setObjectName("tab_btn_container")
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setMaximumHeight(30)
        self.setMinimumWidth(80)
        self.setMaximumWidth(200)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 4, 2)
        layout.setSpacing(3)

        self.btn = QPushButton(title, self)
        self.btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.btn.setStyleSheet(
            "QPushButton { background: transparent; color: rgba(255,255,255,0.85);"
            "border: none; padding: 1px 3px; text-align: left; font-size: 9pt; }"
        )
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.close_btn = QPushButton("x", self)
        self.close_btn.setFixedSize(15, 15)
        self.close_btn.setStyleSheet(
            "QPushButton { background: transparent; color: rgba(255,255,255,0.4);"
            "border: none; font-size: 9pt; padding: 0px; border-radius: 7px; }"
            "QPushButton:hover { color: rgba(255,255,255,0.9); background: rgba(255,255,255,0.12); }"
        )
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        layout.addWidget(self.btn)
        layout.addWidget(self.close_btn)

        self.btn.clicked.connect(lambda: self.clicked.emit(self.index))
        self.close_btn.clicked.connect(lambda: self.close_clicked.emit(self.index))

        self.set_active(False)

    def sizeHint(self) -> QSize:
        return QSize(120, 30)

    def minimumSizeHint(self) -> QSize:
        return QSize(80, 30)

    def set_title(self, title: str) -> None:
        display = title[:22] + "..." if len(title) > 22 else title
        self.btn.setText(display or "New Tab")
        self.btn.setToolTip(title)

    def set_active(self, active: bool) -> None:
        self.setStyleSheet(self._STYLE_ACTIVE if active else self._STYLE_INACTIVE)


class TabPanel(QWidget):

    tab_selected = Signal(int)
    tab_close_requested = Signal(int)
    new_tab_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMaximumHeight(38)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)

        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self.scroll.setMaximumHeight(34)

        self.container = QWidget()
        self.container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.container.setStyleSheet("background: transparent;")

        self.hbox = QHBoxLayout(self.container)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.hbox.setSpacing(3)
        self.hbox.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll, 1)

        self.new_btn = QPushButton("+")
        self.new_btn.setFixedSize(26, 26)
        self.new_btn.setStyleSheet(
            "QPushButton { background: rgba(255,255,255,0.07); border-radius: 5px;"
            "color: white; font-size: 14px; border: 1px solid rgba(255,255,255,0.08); }"
            "QPushButton:hover { background: rgba(255,255,255,0.13); }"
            "QPushButton:pressed { background: rgba(74,110,255,0.35); }"
        )
        self.new_btn.setToolTip("New Tab (Ctrl+T)")
        self.new_btn.clicked.connect(lambda: self.new_tab_requested.emit())
        layout.addWidget(self.new_btn)

        self._buttons: list[_TabButton] = []
        self._current_index: int = -1

    def sync_with_tab_manager(self, tab_manager) -> None:
        for btn in self._buttons:
            btn.clicked.disconnect()
            btn.close_clicked.disconnect()
            btn.setParent(None)
            btn.deleteLater()
        self._buttons.clear()

        count = tab_manager.count()
        for i in range(count):
            raw = tab_manager.tabText(i) or f"Tab {i + 1}"
            b = _TabButton(i, raw, parent=self.container)
            b.set_title(raw)
            b.clicked.connect(self._on_tab_clicked)
            b.close_clicked.connect(self._on_tab_close_clicked)
            self.hbox.addWidget(b)
            self._buttons.append(b)

        cur = tab_manager.currentIndex()
        self.set_current_index(cur)

    def _on_tab_clicked(self, index: int) -> None:
        self.tab_selected.emit(index)

    def _on_tab_close_clicked(self, index: int) -> None:
        self.tab_close_requested.emit(index)

    def set_current_index(self, index: int) -> None:
        self._current_index = index
        for btn in self._buttons:
            btn.set_active(btn.index == index)

    def update_tab_title(self, index: int, title: str) -> None:
        for btn in self._buttons:
            if btn.index == index:
                btn.set_title(title)
                break


__all__ = ["TabPanel"]
