from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame

from app.titlebar import TitleBar
from app.tabs import TabManager
from app.tab_panel import TabPanel
from app.effects import apply_acrylic_to_widget


logger = logging.getLogger(__name__)


class AcrylicBackgroundBrowser(QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("GBrowser")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1200, 780)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(8)

        self.titlebar = TitleBar(self)
        outer.addWidget(self.titlebar)

        self.tab_panel = TabPanel(self)
        outer.addWidget(self.tab_panel)

        frame = QFrame()
        frame.setObjectName("web_frame")
        frame.setStyleSheet("QFrame#web_frame { background:white; border-radius:12px; }")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = TabManager(self)
        try:
            self.tabs.tabBar().hide()
        except Exception:
            pass

        frame_layout.addWidget(self.tabs)
        outer.addWidget(frame)

        self.titlebar.back.clicked.connect(lambda: self._safe_call("back"))
        self.titlebar.fwd.clicked.connect(lambda: self._safe_call("forward"))
        self.titlebar.reload.clicked.connect(lambda: self._safe_call("reload"))
        self.titlebar.url.returnPressed.connect(self.navigate_to_url)
        self.titlebar.new_tab.clicked.connect(self.add_new_tab)

        self.titlebar.min.clicked.connect(self.showMinimized)
        self.titlebar.max.clicked.connect(self.toggle_max_restore)
        self.titlebar.close.clicked.connect(self.close)

        self.tabs.currentChanged.connect(self._on_current_changed)
        self.tabs.tab_url_changed.connect(self._on_tab_url_changed)
        self.tabs.tab_title_changed.connect(self._on_tab_title_changed)

        self.tab_panel.tab_selected.connect(self._on_tab_panel_selected)
        self.tab_panel.tab_close_requested.connect(self._on_tab_panel_close_requested)
        self.tab_panel.new_tab_requested.connect(lambda: self.add_new_tab())

        self.add_new_tab("https://www.google.com", "Google")

    def _safe_call(self, method_name: str) -> None:
        try:
            view = self.tabs.current_view()
            if hasattr(view, method_name):
                getattr(view, method_name)()
        except Exception:
            logger.exception("Error while performing %s on the current view", method_name)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        try:
            apply_acrylic_to_widget(self, 0x661F2937)
        except Exception:
            logger.exception("Failed to apply acrylic")

    def toggle_max_restore(self) -> None:
        self.showNormal() if self.isMaximized() else self.showMaximized()

    def navigate_to_url(self) -> None:
        text = self.titlebar.url.text().strip()
        if not text:
            return
        if not text.startswith(("http://", "https://")):
            text = "https://" + text
        url = QUrl(text)
        if url.isValid():
            self.tabs.open_url_in_current(url)

    def add_new_tab(self, url: str = "https://www.google.com", label: str = "New Tab") -> None:
        index = self.tabs.add_tab(url, label)
        self.tab_panel.sync_with_tab_manager(self.tabs)
        try:
            current_url = self.tabs.current_view().url().toString()
            self.titlebar.url.setText(current_url)
        except Exception:
            pass

    def _on_current_changed(self, index: int) -> None:
        try:
            current_url = self.tabs.current_view().url().toString()
            self.titlebar.url.setText(current_url)
        except Exception:
            self.titlebar.url.setText("")
        self.tab_panel.set_current_index(index)

    def _on_tab_url_changed(self, index: int, qurl) -> None:
        if index == self.tabs.currentIndex():
            self.titlebar.url.setText(qurl.toString())

    def _on_tab_title_changed(self, index: int, title: str) -> None:
        self.tab_panel.update_tab_title(index, title)

    def _on_tab_panel_selected(self, index: int) -> None:
        if 0 <= index < self.tabs.count():
            self.tabs.setCurrentIndex(index)

    def _on_tab_panel_close_requested(self, index: int) -> None:
        self.tabs._on_tab_close_requested(index)
        self.tab_panel.sync_with_tab_manager(self.tabs)


__all__ = ["AcrylicBackgroundBrowser"]