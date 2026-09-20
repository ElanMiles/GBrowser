from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QUrl, Signal, QStandardPaths
from PySide6.QtGui import QAction, QGuiApplication
from PySide6.QtWidgets import (
    QMenu, QDialog, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (
    QWebEngineDownloadRequest, QWebEngineProfile, QWebEngineSettings
)


class BrowserView(QWebEngineView):

    new_tab_requested = Signal(QUrl)
    download_requested = Signal(object)
    fullscreen_requested = Signal(bool)
    load_progress_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        s = self.settings()
        s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)

        self.page().fullScreenRequested.connect(self._on_fullscreen_requested)

        profile: QWebEngineProfile = self.page().profile()
        profile.downloadRequested.connect(self._on_download_requested)

        self.loadProgress.connect(self.load_progress_changed)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

    def _on_fullscreen_requested(self, request) -> None:
        request.accept()
        self.fullscreen_requested.emit(request.toggleOn())

    def _on_download_requested(self, download: QWebEngineDownloadRequest) -> None:
        suggested_name = getattr(download, 'suggestedFileName', lambda: '')()
        if not suggested_name:
            suggested_name = download.url().fileName() or "download"

        downloads_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DownloadLocation
        )
        if not downloads_dir:
            downloads_dir = str(Path.home() / "Downloads")

        target = os.path.join(downloads_dir, suggested_name)
        base, ext = os.path.splitext(target)
        i = 1
        while os.path.exists(target):
            target = f"{base} ({i}){ext}"
            i += 1

        download.setDownloadDirectory(downloads_dir)
        download.setDownloadFileName(os.path.basename(target))
        download.accept()

        self.download_requested.emit(download)

    def _on_context_menu(self, pos) -> None:
        hit = self.lastContextMenuRequest()

        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background:#1e2030; color:#e8e8f0; border:1px solid rgba(255,255,255,0.1);"
            "border-radius:8px; padding:4px; }"
            "QMenu::item { padding:6px 20px; border-radius:4px; }"
            "QMenu::item:selected { background:rgba(74,110,255,0.35); }"
            "QMenu::separator { height:1px; background:rgba(255,255,255,0.08); margin:4px 8px; }"
        )

        back_act = QAction("Back", self)
        forward_act = QAction("Forward", self)
        reload_act = QAction("Reload", self)
        open_new_tab_act = QAction("Open Link in New Tab", self)
        copy_link_act = QAction("Copy Link Address", self)
        copy_text_act = QAction("Copy", self)
        save_page_act = QAction("Save Page As...", self)
        view_source_act = QAction("View Page Source", self)
        inspect_act = QAction("Inspect Element", self)

        back_act.setEnabled(self.history().canGoBack())
        forward_act.setEnabled(self.history().canGoForward())

        has_link = hit is not None and not hit.linkUrl().isEmpty()
        open_new_tab_act.setEnabled(has_link)
        copy_link_act.setEnabled(has_link)

        menu.addAction(back_act)
        menu.addAction(forward_act)
        menu.addAction(reload_act)
        menu.addSeparator()
        if has_link:
            menu.addAction(open_new_tab_act)
            menu.addAction(copy_link_act)
            menu.addSeparator()
        menu.addAction(copy_text_act)
        menu.addSeparator()
        menu.addAction(save_page_act)
        menu.addAction(view_source_act)
        menu.addSeparator()
        menu.addAction(inspect_act)

        action = menu.exec(self.mapToGlobal(pos))
        if action is None:
            return

        if action == back_act:
            self.back()
        elif action == forward_act:
            self.forward()
        elif action == reload_act:
            self.reload()
        elif action == open_new_tab_act and has_link:
            self.new_tab_requested.emit(hit.linkUrl())
        elif action == copy_link_act and has_link:
            QGuiApplication.clipboard().setText(hit.linkUrl().toString())
        elif action == copy_text_act:
            self.page().triggerAction(self.page().WebAction.Copy)
        elif action == save_page_act:
            self._save_page()
        elif action == view_source_act:
            self._view_source_dialog()
        elif action == inspect_act:
            self.page().triggerAction(self.page().WebAction.InspectElement)

    def _save_page(self) -> None:
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Page", str(Path.home() / "page.html"), "HTML Files (*.html)"
        )
        if path:
            self.page().save(path)

    def _view_source_dialog(self) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle("Page Source")
        dlg.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dlg.resize(900, 650)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(8, 8, 8, 8)

        te = QTextEdit(dlg)
        te.setReadOnly(True)
        te.setStyleSheet(
            "background:#0d1117; color:#c9d1d9; font-family:'Consolas','Courier New',monospace;"
            "font-size:10pt; border:none;"
        )
        layout.addWidget(te)

        btn_row = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.close)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        self.page().toHtml(te.setPlainText)
        dlg.exec()

    def createWindow(self, _type):
        new_view = BrowserView()
        new_view.urlChanged.connect(
            lambda u: self.new_tab_requested.emit(u) if not u.isEmpty() else None
        )
        return new_view

    def open_url(self, url: str | QUrl) -> None:
        q = QUrl(url) if isinstance(url, str) else url
        if q.isValid():
            self.setUrl(q)

    def zoom_in(self) -> None:
        self.setZoomFactor(round(min(self.zoomFactor() + 0.1, 5.0), 1))

    def zoom_out(self) -> None:
        self.setZoomFactor(round(max(self.zoomFactor() - 0.1, 0.25), 1))

    def zoom_reset(self) -> None:
        self.setZoomFactor(1.0)


__all__ = ["BrowserView"]
