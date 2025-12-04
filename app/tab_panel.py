from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QScrollArea,
    QSizePolicy
)


class _TabButton(QWidget):
    
    clicked = Signal(int)
    close_clicked = Signal(int)
    
    def __init__(self, index: int, title: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.index = index
        self._title = title
        self._tab_panel = parent 
        
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setMaximumHeight(30)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)
        
        self.btn = QPushButton(title, self)
        self.btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.btn.setStyleSheet("""
            QPushButton { 
                background: transparent; 
                color: rgba(255,255,255,0.9); 
                border: none; 
                padding: 2px 4px;
                text-align: left;
            }
        """)
        self.btn.setCursor(Qt.PointingHandCursor)
        
        self.close_btn = QPushButton("✕", self) 
        self.close_btn.setFixedSize(16, 16)
        self.close_btn.setStyleSheet("""
            QPushButton { 
                background: transparent; 
                color: rgba(255,255,255,0.6); 
                border: none; 
                font-size: 10px;
                padding: 0px;
            }
            QPushButton:hover {
                color: rgba(255,255,255,0.9);
                background: rgba(255,255,255,0.1);
                border-radius: 8px;
            }
        """)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        
        layout.addWidget(self.btn)
        layout.addWidget(self.close_btn)
        
        self.btn.clicked.connect(self._on_clicked)
        self.close_btn.clicked.connect(self._on_close_clicked)

    def _on_clicked(self):
        self.clicked.emit(self.index)  

    def _on_close_clicked(self):
        self.close_clicked.emit(self.index)  

    def sizeHint(self) -> QSize:
        return QSize(100, 30)

    def minimumSizeHint(self) -> QSize:
        return QSize(80, 30)

    def set_title(self, title: str) -> None:
        self._title = title
        self.btn.setText(title)

    def set_active(self, active: bool) -> None:
        if active:
            self.setStyleSheet("""
                background: rgba(255,255,255,0.06); 
                border-radius: 4px;
                border-bottom: 2px solid #4a9eff;
            """)
        else:
            self.setStyleSheet("""
                _TabButton:hover {
                    background: rgba(255,255,255,0.03);
                    border-radius: 4px;
                }
            """)


class TabPanel(QWidget):
    
    tab_selected = Signal(int)
    tab_close_requested = Signal(int)
    new_tab_requested = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.setMaximumHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)
        
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("""
            QScrollArea { 
                background: transparent; 
                border: none; 
            }
        """)
        self.scroll.setMaximumHeight(36)
        
        self.container = QWidget()
        self.container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.hbox = QHBoxLayout(self.container)
        self.hbox.setContentsMargins(2, 2, 2, 2)
        self.hbox.setSpacing(3)
        self.hbox.setAlignment(Qt.AlignLeft)
        
        self.scroll.setWidget(self.container)
        
        layout.addWidget(self.scroll, 1)
        
        self.new_btn = QPushButton("+")
        self.new_btn.setFixedSize(24, 24)
        self.new_btn.setStyleSheet("""
            QPushButton { 
                background: rgba(255,255,255,0.06); 
                border-radius: 4px; 
                color: white; 
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.1);
            }
        """)
        self.new_btn.clicked.connect(lambda: self.new_tab_requested.emit())
        layout.addWidget(self.new_btn)
        
        self._buttons: list[_TabButton] = []
        self._current_index: int = -1

    def sync_with_tab_manager(self, tab_manager) -> None:
        # Удаляем старые кнопки
        for btn in self._buttons:
            btn.clicked.disconnect()
            btn.close_clicked.disconnect()
            btn.setParent(None)
            btn.deleteLater()
        
        self._buttons.clear()
        
        count = tab_manager.count()
        for i in range(count):
            title = tab_manager.tabText(i) or f"Tab {i+1}"
            b = _TabButton(i, title, parent=self.container)
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