from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QUrl, QSettings, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel

from app.titlebar import TitleBar
from app.tabs import TabManager
from app.tab_panel import TabPanel
from app.find_bar import FindBar
from app.settings import SettingsDialog
from app.effects import apply_acrylic_to_widget, remove_acrylic


logger = logging.getLogger(__name__)

_SEARCH_ENGINES = {
    "Google": "https://www.google.com/search?q=",
    "Bing": "https://www.bing.com/search?q=",
    "DuckDuckGo": "https://duckduckgo.com/?q=",
    "YouTube": "https://www.youtube.com/results?search_query=",
}


def _resolve_home_url() -> str:
    here = Path(__file__).resolve().parent.parent
    html = here / "ui" / "home.html"
    if html.exists():
        return QUrl.fromLocalFile(str(html)).toString()
    return "https://www.google.com"


class AcrylicBackgroundBrowser(QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("GBrowser")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(1280, 800)

        self._q_settings = QSettings("GBrowser", "Main")
        self._acrylic_color: int = self._q_settings.value("acrylic_color", 0x661F2937, type=int)
        self._theme: str = self._q_settings.value("theme", "Dark", type=str)
        self._home_page: str = self._q_settings.value("home_page", "", type=str)
        self._system_transparency: bool = self._q_settings.value("system_transparency", True, type=bool)
        self._default_zoom: float = float(self._q_settings.value("default_zoom", 1.0, type=float))
        self._search_engine: str = self._q_settings.value("search_engine", "Google", type=str)

        self._internal_home_url: str = _resolve_home_url()
        self._fullscreen_active: bool = False
        self._was_maximized: bool = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(6)

        self.titlebar = TitleBar(self)
        outer.addWidget(self.titlebar)

        self.tab_panel = TabPanel(self)
        outer.addWidget(self.tab_panel)

        frame = QFrame()
        frame.setObjectName("web_frame")
        frame.setStyleSheet(
            "QFrame#web_frame { background: #0d0d1a; border-radius: 10px; }"
        )
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        self.tabs = TabManager(self)
        try:
            self.tabs.tabBar().hide()
        except Exception:
            pass

        self.find_bar = FindBar(self)

        frame_layout.addWidget(self.tabs)
        frame_layout.addWidget(self.find_bar)
        outer.addWidget(frame)

        self._setup_signals()
        self._setup_shortcuts()

        self.add_new_tab(label="Home")

    def _setup_signals(self) -> None:
        self.titlebar.back.clicked.connect(lambda: self._current_action("back"))
        self.titlebar.fwd.clicked.connect(lambda: self._current_action("forward"))
        self.titlebar.reload.clicked.connect(self._on_reload_clicked)
        self.titlebar.home_btn.clicked.connect(self.go_home)
        self.titlebar.url.returnPressed.connect(self.navigate_to_url)
        self.titlebar.settings_btn.clicked.connect(self.open_settings)
        self.titlebar.find_clicked.connect(self.toggle_find_bar)

        self.titlebar.min_btn.clicked.connect(self.showMinimized)
        self.titlebar.max_btn.clicked.connect(self.toggle_max_restore)
        self.titlebar.close_btn.clicked.connect(self.close)

        self.tabs.currentChanged.connect(self._on_current_changed)
        self.tabs.tab_url_changed.connect(self._on_tab_url_changed)
        self.tabs.tab_title_changed.connect(self._on_tab_title_changed)
        self.tabs.tab_load_progress.connect(self._on_tab_load_progress)
        self.tabs.fullscreen_requested.connect(self._on_fullscreen_requested)

        self.tab_panel.tab_selected.connect(self._on_tab_panel_selected)
        self.tab_panel.tab_close_requested.connect(self._on_tab_panel_close_requested)
        self.tab_panel.new_tab_requested.connect(lambda: self.add_new_tab())

        self.find_bar.closed.connect(lambda: self.titlebar.url.setFocus())

    def _setup_shortcuts(self) -> None:
        shortcuts = [
            (QKeySequence("Ctrl+T"),        self.add_new_tab),
            (QKeySequence("Ctrl+W"),        self._close_current_tab),
            (QKeySequence("Ctrl+R"),        lambda: self._current_action("reload")),
            (QKeySequence("F5"),            lambda: self._current_action("reload")),
            (QKeySequence("Ctrl+L"),        self._focus_url_bar),
            (QKeySequence("Ctrl+F"),        self.toggle_find_bar),
            (QKeySequence("Ctrl+Home"),     self.go_home),
            (QKeySequence("Ctrl+Plus"),     self._zoom_in),
            (QKeySequence("Ctrl+="),        self._zoom_in),
            (QKeySequence("Ctrl+Minus"),    self._zoom_out),
            (QKeySequence("Ctrl+0"),        self._zoom_reset),
            (QKeySequence("Alt+Left"),      lambda: self._current_action("back")),
            (QKeySequence("Alt+Right"),     lambda: self._current_action("forward")),
            (QKeySequence("Ctrl+Tab"),      self._next_tab),
            (QKeySequence("Ctrl+Shift+Tab"), self._prev_tab),
            (QKeySequence("F11"),           self._toggle_fullscreen),
            (QKeySequence("Escape"),        self._on_escape),
            (QKeySequence("Ctrl+1"),        lambda: self._switch_tab(0)),
            (QKeySequence("Ctrl+2"),        lambda: self._switch_tab(1)),
            (QKeySequence("Ctrl+3"),        lambda: self._switch_tab(2)),
            (QKeySequence("Ctrl+4"),        lambda: self._switch_tab(3)),
            (QKeySequence("Ctrl+5"),        lambda: self._switch_tab(4)),
            (QKeySequence("Ctrl+6"),        lambda: self._switch_tab(5)),
            (QKeySequence("Ctrl+7"),        lambda: self._switch_tab(6)),
            (QKeySequence("Ctrl+8"),        lambda: self._switch_tab(7)),
            (QKeySequence("Ctrl+9"),        lambda: self._switch_tab_last()),
        ]
        for key, slot in shortcuts:
            sc = QShortcut(key, self)
            sc.activated.connect(slot)

    def _current_action(self, method: str) -> None:
        try:
            view = self.tabs.current_view()
            if hasattr(view, method):
                getattr(view, method)()
        except Exception:
            logger.exception("Action %s failed", method)

    def _on_reload_clicked(self) -> None:
        try:
            view = self.tabs.current_view()
            if view.url().toString() in ("", "about:blank"):
                self.go_home()
            else:
                view.reload()
        except Exception:
            pass

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._apply_acrylic()

    def _apply_acrylic(self) -> None:
        if self._system_transparency:
            try:
                apply_acrylic_to_widget(self, self._acrylic_color)
            except Exception:
                logger.exception("Failed to apply acrylic")
        else:
            try:
                remove_acrylic(int(self.winId()))
            except Exception:
                logger.exception("Failed to remove acrylic")

    def toggle_max_restore(self) -> None:
        self.showNormal() if self.isMaximized() else self.showMaximized()

    def go_home(self) -> None:
        home = self._home_page if self._home_page else self._internal_home_url
        self.tabs.open_url_in_current(home)

    def navigate_to_url(self) -> None:
        text = self.titlebar.url.text().strip()
        if not text:
            return

        if text.startswith(("http://", "https://", "file://", "ftp://", "about:")):
            url_str = text
        elif "." in text and " " not in text:
            url_str = "https://" + text
        else:
            engine_base = _SEARCH_ENGINES.get(self._search_engine, _SEARCH_ENGINES["Google"])
            from urllib.parse import quote_plus
            url_str = engine_base + quote_plus(text)

        url = QUrl(url_str)
        if url.isValid():
            self.tabs.open_url_in_current(url)

    def add_new_tab(self, url: Optional[str] = None, label: str = "New Tab") -> None:
        home = self._home_page if self._home_page else self._internal_home_url
        target_url = url if url is not None else home

        index = self.tabs.add_tab(target_url, label)

        if self._default_zoom != 1.0:
            QTimer.singleShot(200, lambda: self._apply_zoom_to_current())

        self.tab_panel.sync_with_tab_manager(self.tabs)
        self._update_url_bar()

    def _apply_zoom_to_current(self) -> None:
        try:
            self.tabs.current_view().setZoomFactor(self._default_zoom)
            self.titlebar.set_zoom(self._default_zoom)
        except Exception:
            pass

    def _close_current_tab(self) -> None:
        idx = self.tabs.currentIndex()
        self.tabs.close_tab(idx)
        self.tab_panel.sync_with_tab_manager(self.tabs)

    def _focus_url_bar(self) -> None:
        self.titlebar.url.setFocus()
        self.titlebar.url.selectAll()

    def toggle_find_bar(self) -> None:
        if self.find_bar.isVisible():
            self.find_bar.hide_bar()
        else:
            try:
                self.find_bar.set_view(self.tabs.current_view())
            except Exception:
                pass
            self.find_bar.show_bar()

    def _zoom_in(self) -> None:
        try:
            tab = self.tabs.current_tab()
            if tab:
                tab.zoom_in()
                self.titlebar.set_zoom(tab.zoom_factor())
        except Exception:
            pass

    def _zoom_out(self) -> None:
        try:
            tab = self.tabs.current_tab()
            if tab:
                tab.zoom_out()
                self.titlebar.set_zoom(tab.zoom_factor())
        except Exception:
            pass

    def _zoom_reset(self) -> None:
        try:
            tab = self.tabs.current_tab()
            if tab:
                tab.zoom_reset()
                self.titlebar.set_zoom(1.0)
        except Exception:
            pass

    def _next_tab(self) -> None:
        if self.tabs.count() > 1:
            self.tabs.setCurrentIndex((self.tabs.currentIndex() + 1) % self.tabs.count())

    def _prev_tab(self) -> None:
        if self.tabs.count() > 1:
            self.tabs.setCurrentIndex((self.tabs.currentIndex() - 1) % self.tabs.count())

    def _switch_tab(self, index: int) -> None:
        if 0 <= index < self.tabs.count():
            self.tabs.setCurrentIndex(index)

    def _switch_tab_last(self) -> None:
        self.tabs.setCurrentIndex(self.tabs.count() - 1)

    def _toggle_fullscreen(self) -> None:
        if self._fullscreen_active:
            self._exit_fullscreen()
        else:
            self._enter_fullscreen()

    def _enter_fullscreen(self) -> None:
        self._was_maximized = self.isMaximized()
        self._fullscreen_active = True
        self.titlebar.hide()
        self.tab_panel.hide()
        self.showFullScreen()

    def _exit_fullscreen(self) -> None:
        self._fullscreen_active = False
        self.titlebar.show()
        self.tab_panel.show()
        if self._was_maximized:
            self.showMaximized()
        else:
            self.showNormal()

    def _on_fullscreen_requested(self, toggle_on: bool) -> None:
        if toggle_on:
            self._enter_fullscreen()
        else:
            self._exit_fullscreen()

    def _on_escape(self) -> None:
        if self._fullscreen_active:
            self._exit_fullscreen()
        elif self.find_bar.isVisible():
            self.find_bar.hide_bar()

    def _on_current_changed(self, index: int) -> None:
        self._update_url_bar()
        self.tab_panel.set_current_index(index)
        try:
            view = self.tabs.current_view()
            self.find_bar.set_view(view)
            self.titlebar.set_zoom(view.zoomFactor())
            self.titlebar.set_progress(0)
        except Exception:
            pass

    def _update_url_bar(self) -> None:
        try:
            url_str = self.tabs.current_view().url().toString()
            if url_str in ("about:blank", ""):
                self.titlebar.url.clear()
            else:
                self.titlebar.url.setText(url_str)
            self.titlebar.set_secure(url_str.startswith("https://"))
        except Exception:
            self.titlebar.url.clear()

    def _on_tab_url_changed(self, index: int, qurl: QUrl) -> None:
        if index == self.tabs.currentIndex():
            url_str = qurl.toString()
            if url_str not in ("about:blank", ""):
                self.titlebar.url.setText(url_str)
            else:
                self.titlebar.url.clear()
            self.titlebar.set_secure(url_str.startswith("https://"))
            self.titlebar.back.setEnabled(True)
            self.titlebar.fwd.setEnabled(True)

    def _on_tab_title_changed(self, index: int, title: str) -> None:
        self.tab_panel.update_tab_title(index, title)
        if index == self.tabs.currentIndex() and title:
            self.titlebar.set_title(title)

    def _on_tab_load_progress(self, index: int, progress: int) -> None:
        if index == self.tabs.currentIndex():
            self.titlebar.set_progress(progress)

    def _on_tab_panel_selected(self, index: int) -> None:
        if 0 <= index < self.tabs.count():
            self.tabs.setCurrentIndex(index)

    def _on_tab_panel_close_requested(self, index: int) -> None:
        self.tabs.close_tab(index)
        self.tab_panel.sync_with_tab_manager(self.tabs)

    def open_settings(self) -> None:
        dialog = SettingsDialog(
            self,
            initial_acrylic_color=self._acrylic_color,
            initial_home_page=self._home_page,
            initial_theme=self._theme,
            initial_transparency=self._system_transparency,
            initial_default_zoom=self._default_zoom,
            initial_search_engine=self._search_engine,
        )
        dialog.settings_saved.connect(self.apply_settings)
        dialog.exec()

    def apply_settings(self, s: dict) -> None:
        self._acrylic_color = s["acrylic_color"]
        self._theme = s["theme"]
        self._home_page = s["home_page"]
        self._system_transparency = s["system_transparency"]
        self._default_zoom = s["default_zoom"]
        self._search_engine = s["search_engine"]

        self._q_settings.setValue("acrylic_color", self._acrylic_color)
        self._q_settings.setValue("theme", self._theme)
        self._q_settings.setValue("home_page", self._home_page)
        self._q_settings.setValue("system_transparency", self._system_transparency)
        self._q_settings.setValue("default_zoom", self._default_zoom)
        self._q_settings.setValue("search_engine", self._search_engine)

        self._apply_acrylic()


__all__ = ["AcrylicBackgroundBrowser"]
