from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QProgressBar
)

from app.icon_button import IconButton


class TitleBar(QWidget):

    home_clicked = Signal()
    find_clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.parent_window = parent
        self._drag_offset: Optional[object] = None
        self.setFixedHeight(54)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        row_widget = QWidget()
        layout = QHBoxLayout(row_widget)
        layout.setContentsMargins(12, 5, 10, 5)
        layout.setSpacing(8)

        self.icon = QLabel("GB")
        self.icon.setStyleSheet(
            "color:white; font-weight:700; font-size:11pt;"
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 rgba(90,110,255,0.9), stop:1 rgba(150,90,255,0.9));"
            "border-radius:7px; padding:3px 6px;"
        )

        self.title = QLabel("GBrowser")
        self.title.setFont(QFont("Segoe UI", 9))
        self.title.setStyleSheet("color: rgba(255,255,255,0.55);")
        self.title.setMaximumWidth(90)

        self.discord_dot = QLabel()
        self.discord_dot.setFixedSize(8, 8)
        self.discord_dot.setStyleSheet("background: rgba(255,255,255,0.22); border-radius: 4px;")
        self.discord_dot.setToolTip("Discord RPC: disabled")

        nav_cluster = QWidget()
        nav_cluster.setObjectName("nav_cluster")
        nav_cluster.setStyleSheet(
            "QWidget#nav_cluster { background: rgba(255,255,255,0.04); border-radius: 12px; }"
        )
        nav_layout = QHBoxLayout(nav_cluster)
        nav_layout.setContentsMargins(3, 3, 3, 3)
        nav_layout.setSpacing(2)

        self.back = IconButton("back", 30)
        self.back.setToolTip("Back (Alt+Left)")
        self.fwd = IconButton("forward", 30)
        self.fwd.setToolTip("Forward (Alt+Right)")
        self.reload = IconButton("reload", 30)
        self.reload.setToolTip("Reload (F5)")
        self.home_btn = IconButton("home", 30)
        self.home_btn.setToolTip("Home (Ctrl+Home)")

        nav_layout.addWidget(self.back)
        nav_layout.addWidget(self.fwd)
        nav_layout.addWidget(self.reload)
        nav_layout.addWidget(self.home_btn)

        self.url = QLineEdit()
        self.url.setFixedHeight(32)
        self.url.setStyleSheet(
            "QLineEdit { background:rgba(255,255,255,0.08); color:white; border:1px solid rgba(255,255,255,0.10);"
            "border-radius:9px; padding-left:14px; font-size:9.5pt; }"
            "QLineEdit:focus { background:rgba(255,255,255,0.13); border-color:rgba(110,130,255,0.65); }"
        )
        self.url.setPlaceholderText("Search or enter address...")

        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(40)
        self.zoom_label.setStyleSheet("color:rgba(255,255,255,0.4); font-size:8pt;")
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.find_btn = IconButton("find", 30)
        self.find_btn.setToolTip("Find in Page (Ctrl+F)")
        self.find_btn.set_flat_style()

        self.settings_btn = IconButton("settings", 30)
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.set_flat_style()

        self.min_btn = IconButton("minimize", 36)
        self.min_btn.set_flat_style()

        self.max_btn = IconButton("maximize", 36)
        self.max_btn.set_flat_style()

        self.close_btn = IconButton("close", 36)
        self.close_btn.set_danger_style()

        layout.addWidget(self.icon)
        layout.addWidget(self.title)
        layout.addWidget(self.discord_dot)
        layout.addSpacing(6)
        layout.addWidget(nav_cluster)
        layout.addSpacing(6)
        layout.addWidget(self.url, 1)
        layout.addWidget(self.zoom_label)
        layout.addWidget(self.find_btn)
        layout.addWidget(self.settings_btn)
        layout.addSpacing(6)
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
            border = "rgba(60,200,100,0.4)"
        else:
            border = "rgba(255,255,255,0.10)"
        self.url.setStyleSheet(
            "QLineEdit { background:rgba(255,255,255,0.08); color:white;"
            f"border:1px solid {border}; border-radius:9px; padding-left:14px; font-size:9.5pt; }}"
            "QLineEdit:focus { background:rgba(255,255,255,0.13); border-color:rgba(110,130,255,0.65); }"
        )

    def set_zoom(self, factor: float) -> None:
        self.zoom_label.setText(f"{int(factor * 100)}%")

    def set_title(self, text: str) -> None:
        display = text[:14] + "..." if len(text) > 14 else text
        self.title.setText(display)
        self.title.setToolTip(text)

    def set_discord_status(self, connected: bool) -> None:
        if connected:
            self.discord_dot.setStyleSheet("background: rgba(88,196,133,0.9); border-radius: 4px;")
            self.discord_dot.setToolTip("Discord RPC: connected")
        else:
            self.discord_dot.setStyleSheet("background: rgba(255,255,255,0.22); border-radius: 4px;")
            self.discord_dot.setToolTip("Discord RPC: disabled")

    def update_maximize_icon(self, is_maximized: bool) -> None:
        self.max_btn.set_icon_name("restore" if is_maximized else "maximize")

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
                if hasattr(win, "titlebar"):
                    win.titlebar.update_maximize_icon(False)
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