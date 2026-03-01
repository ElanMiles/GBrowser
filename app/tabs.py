from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QMenu

from app.browser_view import BrowserView


class BrowserTab(QWidget):

    new_tab_requested = Signal(QUrl)
    fullscreen_requested = Signal(bool)
    load_progress_changed = Signal(int)

    def __init__(self, url: str = "") -> None:
        super().__init__()
        self.view = BrowserView(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        self.view.new_tab_requested.connect(self.new_tab_requested)
        self.view.fullscreen_requested.connect(self.fullscreen_requested)
        self.view.load_progress_changed.connect(self.load_progress_changed)

        if url:
            q = QUrl(url)
            if not q.isValid() or q.isEmpty():
                q = QUrl("about:blank")
            self.view.setUrl(q)

    def setUrl(self, url: str | QUrl) -> None:
        q = QUrl(url) if isinstance(url, str) else url
        if q.isValid():
            self.view.setUrl(q)

    def url(self) -> QUrl:
        return self.view.url()

    def back(self) -> None:
        self.view.back()

    def forward(self) -> None:
        self.view.forward()

    def reload(self) -> None:
        self.view.reload()

    def zoom_in(self) -> None:
        self.view.zoom_in()

    def zoom_out(self) -> None:
        self.view.zoom_out()

    def zoom_reset(self) -> None:
        self.view.zoom_reset()

    def zoom_factor(self) -> float:
        return self.view.zoomFactor()


class TabManager(QTabWidget):

    tab_url_changed = Signal(int, QUrl)
    tab_title_changed = Signal(int, str)
    tab_load_progress = Signal(int, int)
    fullscreen_requested = Signal(bool)
    new_tab_from_page = Signal(QUrl)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)
        self.tabCloseRequested.connect(self.close_tab)

    def add_tab(self, url: str = "", label: str = "New Tab") -> int:
        tab = BrowserTab(url)
        index = self.addTab(tab, label)
        self.setCurrentIndex(index)

        tab.view.urlChanged.connect(
            lambda q, t=tab: self._on_url_changed(self.indexOf(t), q)
        )
        tab.view.titleChanged.connect(
            lambda title, t=tab: self._on_title_changed(self.indexOf(t), title)
        )
        tab.view.loadProgress.connect(
            lambda p, t=tab: self._on_load_progress(self.indexOf(t), p)
        )
        tab.view.fullscreen_requested.connect(self.fullscreen_requested)
        tab.view.new_tab_requested.connect(self._on_new_tab_from_page)

        return index

    def _on_new_tab_from_page(self, url: QUrl) -> None:
        self.add_tab(url.toString(), "New Tab")
        self.new_tab_from_page.emit(url)

    def current_view(self) -> BrowserView:
        w = self.currentWidget()
        if isinstance(w, BrowserTab):
            return w.view
        raise RuntimeError("Current tab does not contain a BrowserView")

    def current_tab(self) -> Optional[BrowserTab]:
        w = self.currentWidget()
        return w if isinstance(w, BrowserTab) else None

    def open_url_in_current(self, url: str | QUrl) -> None:
        w = self.currentWidget()
        if isinstance(w, BrowserTab):
            w.setUrl(url)

    def close_tab(self, index: int) -> None:
        if self.count() <= 1:
            self.removeTab(index)
            self.add_tab("", "Home")
        else:
            self.removeTab(index)

    def _on_url_changed(self, index: int, qurl: QUrl) -> None:
        if 0 <= index < self.count():
            self.tab_url_changed.emit(index, qurl)

    def _on_title_changed(self, index: int, title: str) -> None:
        if 0 <= index < self.count():
            display = title[:30] + "..." if len(title) > 30 else title
            self.setTabText(index, display or "New Tab")
            self.tab_title_changed.emit(index, title)

    def _on_load_progress(self, index: int, progress: int) -> None:
        if 0 <= index < self.count():
            self.tab_load_progress.emit(index, progress)

    def _on_context_menu(self, pos) -> None:
        tab_index = self.tabAt(pos)
        if tab_index < 0:
            return
        menu = QMenu(self)
        close_action = menu.addAction("Close Tab")
        reload_action = menu.addAction("Reload")
        duplicate_action = menu.addAction("Duplicate Tab")
        menu.addSeparator()
        mute_action = menu.addAction("Mute Tab")

        action = menu.exec(self.mapToGlobal(pos))
        if action is None:
            return

        if action == close_action:
            self.close_tab(tab_index)
        elif action == reload_action:
            w = self.widget(tab_index)
            if isinstance(w, BrowserTab):
                w.reload()
        elif action == duplicate_action:
            w = self.widget(tab_index)
            if isinstance(w, BrowserTab):
                self.add_tab(w.url().toString(), self.tabText(tab_index))
        elif action == mute_action:
            w = self.widget(tab_index)
            if isinstance(w, BrowserTab):
                page = w.view.page()
                page.setAudioMuted(not page.isAudioMuted())


__all__ = ["BrowserTab", "TabManager"]
