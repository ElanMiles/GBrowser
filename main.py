import sys
import ctypes
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QTabWidget
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFont
from PySide6.QtWebEngineWidgets import QWebEngineView


class ACCENT_POLICY(ctypes.Structure):
    _fields_ = [
        ("AccentState", ctypes.c_int),
        ("AccentFlags", ctypes.c_int),
        ("GradientColor", ctypes.c_uint32),
        ("AnimationId", ctypes.c_int)
    ]

class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
    _fields_ = [
        ("Attribute", ctypes.c_int),
        ("Data", ctypes.c_void_p),
        ("SizeOfData", ctypes.c_size_t)
    ]

WCA_ACCENT_POLICY = 19
ACCENT_ENABLE_ACRYLICBLURBEHIND = 4

def enable_acrylic(hwnd, color=0x661F2937):
    try:
        SetAttr = ctypes.windll.user32.SetWindowCompositionAttribute
    except Exception:
        return

    accent = ACCENT_POLICY()
    accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
    accent.AccentFlags = 2
    accent.GradientColor = color

    data = WINDOWCOMPOSITIONATTRIBDATA()
    data.Attribute = WCA_ACCENT_POLICY
    data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.c_void_p)
    data.SizeOfData = ctypes.sizeof(accent)

    try:
        SetAttr(hwnd, ctypes.byref(data))
    except Exception:
        pass



class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self._drag_offset = None
        self.setFixedHeight(46)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)

        self.icon = QLabel("🌐")
        self.title = QLabel("GBrowser")
        self.title.setFont(QFont("Segoe UI", 10))
        self.title.setStyleSheet("color: white")

        self.back = QPushButton("<-")
        self.fwd = QPushButton("->")
        self.reload = QPushButton("⟳")
        for b in (self.back, self.fwd, self.reload):
            b.setFixedSize(28, 28)
            b.setStyleSheet("color:white;background:rgba(255,255,255,0.06);border-radius:6px;")

        self.new_tab = QPushButton("+")
        self.new_tab.setFixedSize(32, 28)
        self.new_tab.setStyleSheet("color:white;background:rgba(255,255,255,0.06);border-radius:6px;")

        self.url = QLineEdit()
        self.url.setFixedHeight(30)
        self.url.setStyleSheet("background:rgba(255,255,255,0.14);color:white;border:none;border-radius:6px;padding-left:8px;")
        self.url.setPlaceholderText("Enter the address and press Enter")

        self.min = QPushButton("–")
        self.max = QPushButton("☐")
        self.close = QPushButton("✕")
        for b in (self.min, self.max, self.close):
            b.setFixedSize(36, 26)
            b.setStyleSheet("color:white;background:transparent;border:none;")

        layout.addWidget(self.icon)
        layout.addWidget(self.title)
        layout.addSpacing(8)
        layout.addWidget(self.back)
        layout.addWidget(self.fwd)
        layout.addWidget(self.reload)
        layout.addWidget(self.new_tab)
        layout.addSpacing(8)
        layout.addWidget(self.url)
        layout.addWidget(self.min)
        layout.addWidget(self.max)
        layout.addWidget(self.close)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            win = self.parent_window
            if win.isMaximized():
                rel_x = event.position().x() / self.width()
                self._drag_offset = ('max', rel_x)
            else:
                self._drag_offset = event.globalPosition().toPoint() - win.frameGeometry().topLeft()
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self._drag_offset is not None:
            win = self.parent_window
            if isinstance(self._drag_offset, tuple):
                rel_x = self._drag_offset[1]
                win.showNormal()
                restored_w = win.width()
                offset = int(restored_w * rel_x)
                self._drag_offset = event.globalPosition().toPoint() - QPoint(offset, 10)
            win.move(event.globalPosition().toPoint() - self._drag_offset)
        return super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.parent_window.toggle_max_restore()
        return super().mouseDoubleClickEvent(event)



class AcrylicBackgroundBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GBrowser")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1200, 780)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(0)

        self.titlebar = TitleBar(self)
        outer.addWidget(self.titlebar)

        frame = QFrame()
        frame.setObjectName("web_frame")
        frame.setStyleSheet("QFrame#web_frame { background:white; border-radius:12px; }")

        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        frame_layout.addWidget(self.tabs)
        outer.addWidget(frame)

        self.titlebar.back.clicked.connect(lambda: self.current().back())
        self.titlebar.fwd.clicked.connect(lambda: self.current().forward())
        self.titlebar.reload.clicked.connect(lambda: self.current().reload())
        self.titlebar.url.returnPressed.connect(self.navigate_to_url)
        self.titlebar.new_tab.clicked.connect(lambda: self.add_new_tab())

        self.titlebar.min.clicked.connect(self.showMinimized)
        self.titlebar.max.clicked.connect(self.toggle_max_restore)
        self.titlebar.close.clicked.connect(self.close)

        self.add_new_tab("https://www.google.com")

    def current(self):
        return self.tabs.currentWidget()

    def showEvent(self, event):
        super().showEvent(event)
        hwnd = int(self.winId())
        enable_acrylic(hwnd, 0x661F2937)

    def toggle_max_restore(self):
        self.showNormal() if self.isMaximized() else self.showMaximized()

    def navigate_to_url(self):
        text = self.titlebar.url.text().strip()
        if text and not text.startswith(("http://", "https://")):
            text = "https://" + text
        self.current().setUrl(text)

    def add_new_tab(self, url="https://google.com", label="New Tab"):
        view = QWebEngineView()
        view.setUrl(url)
        index = self.tabs.addTab(view, label)
        self.tabs.setCurrentIndex(index)

        view.urlChanged.connect(lambda u: self.titlebar.url.setText(u.toString()))
        view.titleChanged.connect(lambda t: self.tabs.setTabText(index, t))

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    w = AcrylicBackgroundBrowser()
    w.show()
    sys.exit(app.exec())
