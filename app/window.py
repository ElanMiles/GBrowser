from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QUrl, QSettings
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame

from app.titlebar import TitleBar
from app.tabs import TabManager
from app.tab_panel import TabPanel
from app.settings import SettingsDialog
from app.effects import apply_acrylic_to_widget, remove_acrylic


logger = logging.getLogger(__name__)


class AcrylicBackgroundBrowser(QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("GBrowser")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1200, 780)

        self.settings = QSettings("GBrowser", "Main")
        self._acrylic_color = self.settings.value("acrylic_color", 0x661F2937, type=int)
        self._theme = self.settings.value("theme", "Dark", type=str)
        self._home_page = self.settings.value("home_page", "https://www.google.com", type=str)
        self._system_transparency = self.settings.value("system_transparency", True, type=bool)

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
        self.titlebar.settings.clicked.connect(self.open_settings)

        self.titlebar.min.clicked.connect(self.showMinimized)
        self.titlebar.max.clicked.connect(self.toggle_max_restore)
        self.titlebar.close.clicked.connect(self.close)

        self.tabs.currentChanged.connect(self._on_current_changed)
        self.tabs.tab_url_changed.connect(self._on_tab_url_changed)
        self.tabs.tab_title_changed.connect(self._on_tab_title_changed)

        self.tab_panel.tab_selected.connect(self._on_tab_panel_selected)
        self.tab_panel.tab_close_requested.connect(self._on_tab_panel_close_requested)
        self.tab_panel.new_tab_requested.connect(lambda: self.add_new_tab())

        self.add_new_tab(self._home_page, "Google")

    def _safe_call(self, method_name: str) -> None:
        try:
            view = self.tabs.current_view()
            if hasattr(view, method_name):
                getattr(view, method_name)()
        except Exception:
            logger.exception("Error while performing %s on the current view", method_name)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._apply_acrylic()

    def _apply_acrylic(self):
        if self._system_transparency:
            try:
                apply_acrylic_to_widget(self, self._acrylic_color)
            except Exception:
                logger.exception("Failed to apply acrylic")
        else:
            try:
                hwnd = int(self.winId())
                remove_acrylic(hwnd)
            except Exception:
                logger.exception("Failed to remove acrylic")

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

    def add_new_tab(self, url: Optional[str] = None, label: str = "New Tab") -> None:
        if url is None:
            url = self._home_page
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

    def open_settings(self) -> None:
        dialog = SettingsDialog(self, self._acrylic_color)
        dialog.theme_combo.setCurrentText(self._theme)
        dialog.home_edit.setText(self._home_page)
        dialog.sys_transparency.setChecked(self._system_transparency)
        dialog.settings_saved.connect(self.apply_settings)
        dialog.exec()

    def apply_settings(self, settings: dict) -> None:
        self._acrylic_color = settings["acrylic_color"]
        self._theme = settings["theme"]
        self._home_page = settings["home_page"]
        self._system_transparency = settings["system_transparency"]

        self.settings.setValue("acrylic_color", self._acrylic_color)
        self.settings.setValue("theme", self._theme)
        self.settings.setValue("home_page", self._home_page)
        self.settings.setValue("system_transparency", self._system_transparency)

        self._apply_acrylic()


__all__ = ["AcrylicBackgroundBrowser"]