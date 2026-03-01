from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox,
    QPushButton, QLineEdit, QCheckBox, QWidget, QFrame
)

from app.effects import apply_acrylic_to_widget


_BASE_RGB = 0x001F2937


class SettingsDialog(QDialog):

    settings_saved = Signal(dict)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        initial_acrylic_color: int = 0x661F2937,
        initial_home_page: str = "",
        initial_theme: str = "Dark",
        initial_transparency: bool = True,
        initial_default_zoom: float = 1.0,
        initial_search_engine: str = "Google",
    ) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.resize(540, 460)

        self._initial_color = initial_acrylic_color
        self._initial_alpha = (initial_acrylic_color >> 24) & 0xFF

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title_lbl = QLabel("Settings")
        title_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Light))
        title_lbl.setStyleSheet("color: white;")
        layout.addWidget(title_lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: rgba(255,255,255,0.1);")
        layout.addWidget(sep)

        lbl_style = "color: rgba(255,255,255,0.8); font-size: 9.5pt;"

        alpha_row = QHBoxLayout()
        alpha_lbl = QLabel("Acrylic transparency:")
        alpha_lbl.setStyleSheet(lbl_style)
        self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setRange(0, 100)
        self.alpha_slider.setValue(int(self._initial_alpha * 100 / 255))
        self.alpha_value_lbl = QLabel(f"{self.alpha_slider.value()}%")
        self.alpha_value_lbl.setStyleSheet(lbl_style)
        self.alpha_value_lbl.setMinimumWidth(38)
        alpha_row.addWidget(alpha_lbl)
        alpha_row.addWidget(self.alpha_slider, 1)
        alpha_row.addWidget(self.alpha_value_lbl)
        layout.addLayout(alpha_row)

        zoom_row = QHBoxLayout()
        zoom_lbl = QLabel("Default zoom:")
        zoom_lbl.setStyleSheet(lbl_style)
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["75%", "90%", "100%", "110%", "125%", "150%", "200%"])
        zoom_val = f"{int(initial_default_zoom * 100)}%"
        idx = self.zoom_combo.findText(zoom_val)
        self.zoom_combo.setCurrentIndex(idx if idx >= 0 else 2)
        zoom_row.addWidget(zoom_lbl)
        zoom_row.addWidget(self.zoom_combo)
        layout.addLayout(zoom_row)

        engine_row = QHBoxLayout()
        engine_lbl = QLabel("Default search engine:")
        engine_lbl.setStyleSheet(lbl_style)
        self.engine_combo = QComboBox()
        self.engine_combo.addItems(["Google", "Bing", "DuckDuckGo", "YouTube"])
        idx = self.engine_combo.findText(initial_search_engine)
        self.engine_combo.setCurrentIndex(idx if idx >= 0 else 0)
        engine_row.addWidget(engine_lbl)
        engine_row.addWidget(self.engine_combo)
        layout.addLayout(engine_row)

        theme_row = QHBoxLayout()
        theme_lbl = QLabel("Theme (Coming Soon):")
        theme_lbl.setStyleSheet(lbl_style)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "Auto"])
        self.theme_combo.setCurrentText(initial_theme)
        theme_row.addWidget(theme_lbl)
        theme_row.addWidget(self.theme_combo)
        layout.addLayout(theme_row)

        home_row = QHBoxLayout()
        home_lbl = QLabel("Home page URL:")
        home_lbl.setStyleSheet(lbl_style)
        self.home_edit = QLineEdit()
        self.home_edit.setPlaceholderText("Leave empty for built-in home page")
        self.home_edit.setText(initial_home_page)
        self.home_edit.setStyleSheet(
            "QLineEdit { background:rgba(255,255,255,0.08); color:white;"
            "border:1px solid rgba(255,255,255,0.15); border-radius:6px; padding:4px 10px; }"
        )
        home_row.addWidget(home_lbl)
        home_row.addWidget(self.home_edit, 1)
        layout.addLayout(home_row)

        self.sys_transparency = QCheckBox("Enable system transparency / acrylic effect")
        self.sys_transparency.setStyleSheet(lbl_style)
        self.sys_transparency.setChecked(initial_transparency)
        layout.addWidget(self.sys_transparency)

        self.restore_tabs = QCheckBox("Restore tabs on startup (Coming Soon)")
        self.restore_tabs.setStyleSheet(lbl_style)
        self.restore_tabs.setEnabled(False)
        layout.addWidget(self.restore_tabs)

        layout.addStretch()

        btn_sep = QFrame()
        btn_sep.setFrameShape(QFrame.Shape.HLine)
        btn_sep.setStyleSheet("color: rgba(255,255,255,0.1);")
        layout.addWidget(btn_sep)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.cancel_btn = QPushButton("Cancel")
        self.save_btn = QPushButton("Save")
        btn_style = (
            "QPushButton { color:white; background:rgba(255,255,255,0.07);"
            "border-radius:6px; border:1px solid rgba(255,255,255,0.1);"
            "padding:5px 18px; font-size:9.5pt; }"
            "QPushButton:hover { background:rgba(255,255,255,0.14); }"
        )
        save_style = (
            "QPushButton { color:white; background:rgba(74,110,255,0.65);"
            "border-radius:6px; border:none; padding:5px 18px; font-size:9.5pt; }"
            "QPushButton:hover { background:rgba(74,110,255,0.9); }"
        )
        self.cancel_btn.setStyleSheet(btn_style)
        self.save_btn.setStyleSheet(save_style)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.save_btn)
        layout.addLayout(btn_row)

        self.alpha_slider.valueChanged.connect(self._on_alpha_changed)
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self._on_save)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        try:
            alpha = (self._initial_color >> 24) & 0xFF
            color = (alpha << 24) | (_BASE_RGB & 0x00FFFFFF)
            apply_acrylic_to_widget(self, color)
        except Exception:
            pass

    def _on_alpha_changed(self, value: int) -> None:
        self.alpha_value_lbl.setText(f"{value}%")
        aa = int(value * 255 / 100) & 0xFF
        color = (aa << 24) | (_BASE_RGB & 0x00FFFFFF)
        try:
            apply_acrylic_to_widget(self, color)
        except Exception:
            pass

    def _on_save(self) -> None:
        value = self.alpha_slider.value()
        aa = int(value * 255 / 100) & 0xFF
        color = (aa << 24) | (_BASE_RGB & 0x00FFFFFF)

        zoom_map = {"75%": 0.75, "90%": 0.9, "100%": 1.0, "110%": 1.1,
                    "125%": 1.25, "150%": 1.5, "200%": 2.0}
        zoom_text = self.zoom_combo.currentText()
        zoom = zoom_map.get(zoom_text, 1.0)

        s = {
            "acrylic_color": color,
            "theme": self.theme_combo.currentText(),
            "home_page": self.home_edit.text().strip(),
            "system_transparency": self.sys_transparency.isChecked(),
            "default_zoom": zoom,
            "search_engine": self.engine_combo.currentText(),
        }
        self.settings_saved.emit(s)
        self.accept()


__all__ = ["SettingsDialog"]
