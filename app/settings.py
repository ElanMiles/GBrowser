from __future__ import annotations

from typing import Dict
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox,
    QPushButton, QLineEdit, QCheckBox, QWidget
)

from app.effects import apply_acrylic_to_widget


class SettingsDialog(QDialog):
    settings_saved = Signal(dict)

    def __init__(self, parent: QWidget | None = None, initial_acrylic_color: int = 0x661F2937) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.resize(520, 360)

        self._base_rgb = 0x001F2937
        self._initial_color = initial_acrylic_color
        self._initial_alpha = (initial_acrylic_color >> 24) & 0xFF

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Settings")
        title.setFont(QFont("Segoe UI", 14))
        title.setStyleSheet("color: white")
        layout.addWidget(title)

        row = QHBoxLayout()
        label = QLabel("Acrylic transparency:")
        label.setStyleSheet("color:white")
        self.alpha_slider = QSlider(Qt.Horizontal)
        self.alpha_slider.setRange(0, 100)
        self.alpha_slider.setValue(int(self._initial_alpha * 100 / 255))
        self.alpha_value_lbl = QLabel(f"{self.alpha_slider.value()}%")
        self.alpha_value_lbl.setStyleSheet("color:white")
        row.addWidget(label)
        row.addWidget(self.alpha_slider, 1)
        row.addWidget(self.alpha_value_lbl)
        layout.addLayout(row)

        row2 = QHBoxLayout()
        theme_lbl = QLabel("Theme (Coming Soon):")
        theme_lbl.setStyleSheet("color:white")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "Auto"])
        row2.addWidget(theme_lbl)
        row2.addWidget(self.theme_combo)
        layout.addLayout(row2)

        row3 = QHBoxLayout()
        home_lbl = QLabel("Home page URL (To apply this change, you need to restart the browser):")
        home_lbl.setStyleSheet("color:white")
        self.home_edit = QLineEdit()
        self.home_edit.setPlaceholderText("https://example.com")
        row3.addWidget(home_lbl)
        row3.addWidget(self.home_edit)
        layout.addLayout(row3)

        self.sys_transparency = QCheckBox("Enable system transparency effects (Disabling this parameter may result in the browser frame being absent)")
        self.sys_transparency.setStyleSheet("color:white")
        self.sys_transparency.setChecked(True)
        layout.addWidget(self.sys_transparency)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.cancel_btn = QPushButton("Cancel")
        self.save_btn = QPushButton("Save")
        for b in (self.cancel_btn, self.save_btn):
            b.setFixedHeight(30)
            b.setStyleSheet("color:white;background:rgba(255,255,255,0.06);border-radius:6px;")
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
            color = (alpha << 24) | (self._base_rgb & 0x00FFFFFF)
            apply_acrylic_to_widget(self, color)
        except Exception:
            pass

    def _on_alpha_changed(self, value: int) -> None:
        self.alpha_value_lbl.setText(f"{value}%")
        aa = int(value * 255 / 100) & 0xFF
        color = (aa << 24) | (self._base_rgb & 0x00FFFFFF)
        try:
            apply_acrylic_to_widget(self, color)
        except Exception:
            pass

    def _on_save(self) -> None:
        value = self.alpha_slider.value()
        aa = int(value * 255 / 100) & 0xFF
        color = (aa << 24) | (self._base_rgb & 0x00FFFFFF)
        settings = {
            "acrylic_color": color,
            "theme": self.theme_combo.currentText(),
            "home_page": self.home_edit.text().strip(),
            "system_transparency": self.sys_transparency.isChecked(),
        }
        self.settings_saved.emit(settings)
        self.accept()


__all__ = ["SettingsDialog"]