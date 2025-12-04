from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QUrl, Signal, Slot
from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QMenu
from PySide6.QtWebEngineWidgets import QWebEngineView


class BrowserTab(QWidget):

    def __init__(self, url: str | QUrl = "about:blank", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.view = QWebEngineView(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        q = QUrl(url) if isinstance(url, str) else url
        if q.isValid():
            self.view.setUrl(q)

    def setUrl(self, url: str | QUrl) -> None:
        q = QUrl(url) if isinstance(url, str) else url
        if q.isValid():
            self.view.setUrl(q)

    def url(self):
        return self.view.url()

    def back(self) -> None:
        self.view.back()

    def forward(self) -> None:
        self.view.forward()

    def reload(self) -> None:
        self.view.reload()


class TabManager(QTabWidget):

    tab_url_changed = Signal(int, QUrl)
    tab_title_changed = Signal(int, str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

        self.tabCloseRequested.connect(self._on_tab_close_requested)

    def add_tab(self, url: str = "https://www.google.com", label: str = "New Tab") -> int:
        tab = BrowserTab(url)
        index = self.addTab(tab, label)
        self.setCurrentIndex(index)

        view = tab.view

        view.urlChanged.connect(lambda q, idx=index: self._on_url_changed(idx, q))
        view.titleChanged.connect(lambda t, idx=index: self._on_title_changed(idx, t))

        return index

    def current_view(self) -> QWebEngineView:
        w = self.currentWidget()
        if isinstance(w, BrowserTab):
            return w.view
        if isinstance(w, QWebEngineView):
            return w
        raise RuntimeError("Current tab does not contain a QWebEngineView")

    def open_url_in_current(self, url: str | QUrl) -> None:
        w = self.currentWidget()
        if isinstance(w, BrowserTab):
            w.setUrl(url)
        elif isinstance(w, QWebEngineView):
            w.setUrl(QUrl(url))

    def _on_url_changed(self, index: int, qurl: QUrl) -> None:
        if 0 <= index < self.count():
            self.tab_url_changed.emit(index, qurl)

    def _on_title_changed(self, index: int, title: str) -> None:
        if 0 <= index < self.count():
            self.setTabText(index, title)
            self.tab_title_changed.emit(index, title)

    def _on_tab_close_requested(self, index: int) -> None:
        if self.count() > 1:
            self.removeTab(index)
        else:
            self.removeTab(index)
            self.add_tab("about:blank", "New Tab")

    def _on_context_menu(self, pos):
        tab_index = self.tabAt(pos)
        if tab_index < 0:
            return
        menu = QMenu(self)
        close_action = menu.addAction("Close Tab")
        reload_action = menu.addAction("Reload")
        duplicate_action = menu.addAction("Duplicate Tab")

        action = menu.exec(self.mapToGlobal(pos))
        if action is None:
            return
        if action == close_action:
            self._on_tab_close_requested(tab_index)
        elif action == reload_action:
            w = self.widget(tab_index)
            if isinstance(w, BrowserTab):
                w.reload()
        elif action == duplicate_action:
            w = self.widget(tab_index)
            if isinstance(w, BrowserTab):
                self.add_tab(w.url().toString(), "Copy")


__all__ = ["BrowserTab", "TabManager"]
