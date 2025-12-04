from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtWidgets import (
    QMenu, QAction, QFileDialog, QDialog, QVBoxLayout, QTextEdit, QMessageBox
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineDownloadItem, QWebEngineProfile
from PySide6.QtCore import QStandardPaths


class BrowserView(QWebEngineView):

    new_tab_requested = Signal(QUrl)
    download_requested = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        s = self.settings()
        try:
            s.setAttribute(s.JavascriptEnabled, True)
            s.setAttribute(s.LocalStorageEnabled, True)
            s.setAttribute(s.PluginsEnabled, False)
        except Exception:
            pass

        profile: QWebEngineProfile = self.page().profile()
        profile.downloadRequested.connect(self._on_download_requested)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

    def _on_download_requested(self, download: QWebEngineDownloadItem) -> None:
        suggested_name = download.path() or download.suggestedFileName()
        downloads_dir = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        if not downloads_dir:
            downloads_dir = str(Path.home() / "Downloads")
        target = os.path.join(downloads_dir, suggested_name)

        base, ext = os.path.splitext(target)
        i = 1
        while os.path.exists(target):
            target = f"{base} ({i}){ext}"
            i += 1

        download.setPath(target)
        download.accept()

        self.download_requested.emit(download)

    def _on_context_menu(self, pos) -> None:
        menu = QMenu(self)

        back_act = QAction("Back", self)
        forward_act = QAction("Forward", self)
        reload_act = QAction("Reload", self)
        open_new_tab_act = QAction("Open in New Tab", self)
        copy_link_act = QAction("Copy Link", self)
        view_source_act = QAction("View Page Source", self)

        back_act.setEnabled(self.history().canGoBack())
        forward_act.setEnabled(self.history().canGoForward())

        menu.addAction(back_act)
        menu.addAction(forward_act)
        menu.addAction(reload_act)
        menu.addSeparator()
        menu.addAction(open_new_tab_act)
        menu.addAction(copy_link_act)
        menu.addSeparator()
        menu.addAction(view_source_act)

        action = menu.exec(self.mapToGlobal(pos))
        if action is None:
            return

        if action == back_act:
            self.back()
        elif action == forward_act:
            self.forward()
        elif action == reload_act:
            self.reload()
        elif action == open_new_tab_act:
            data = self.page().contextMenuData()
            url = data.linkUrl() if data and not data.linkUrl().isEmpty() else self.url()
            self.new_tab_requested.emit(url)
        elif action == copy_link_act:
            data = self.page().contextMenuData()
            url = data.linkUrl() if data and not data.linkUrl().isEmpty() else self.url()
            cb = self.page().profile().clipboard() if hasattr(self.page().profile(), 'clipboard') else None
            # fallback: use Qt clipboard
            from PySide6.QtGui import QGuiApplication
            QGuiApplication.clipboard().setText(url.toString())
        elif action == view_source_act:
            self.view_source_dialog()

    def view_source_dialog(self) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle("Page Source")
        dlg.setAttribute(Qt.WA_DeleteOnClose)
        dlg.resize(800, 600)
        layout = QVBoxLayout(dlg)
        te = QTextEdit(dlg)
        te.setReadOnly(True)
        layout.addWidget(te)

        def _set_html(html: str) -> None:
            te.setPlainText(html)

        self.page().toHtml(_set_html)
        dlg.exec()

    def createWindow(self, _type):
        new_view = BrowserView(self.parent())

        def _on_url_changed(u: QUrl) -> None:
            if not u.isEmpty():
                self.new_tab_requested.emit(u)

        new_view.urlChanged.connect(_on_url_changed)
        return new_view

    def open_url(self, url: str | QUrl) -> None:
        q = QUrl(url) if isinstance(url, str) else url
        if q.isValid():
            self.setUrl(q)


__all__ = ["BrowserView"]
