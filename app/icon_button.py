from __future__ import annotations

import math
from typing import Optional

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath
from PySide6.QtWidgets import QPushButton, QWidget


class IconButton(QPushButton):

    def __init__(self, icon_name: str, size: int = 30, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._icon_name = icon_name
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_default_style()

    def set_default_style(self) -> None:
        self.setStyleSheet(
            "QPushButton { background: rgba(255,255,255,0.06); border-radius: 8px; border: none; }"
            "QPushButton:hover { background: rgba(255,255,255,0.14); }"
            "QPushButton:pressed { background: rgba(96,130,255,0.45); }"
            "QPushButton:disabled { background: rgba(255,255,255,0.03); }"
        )

    def set_flat_style(self) -> None:
        self.setStyleSheet(
            "QPushButton { background: transparent; border-radius: 6px; border: none; }"
            "QPushButton:hover { background: rgba(255,255,255,0.10); }"
        )

    def set_danger_style(self) -> None:
        self.setStyleSheet(
            "QPushButton { background: transparent; border-radius: 6px; border: none; }"
            "QPushButton:hover { background: rgba(230,70,70,0.85); }"
        )

    def set_icon_name(self, icon_name: str) -> None:
        self._icon_name = icon_name
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        enabled = self.isEnabled()
        base_color = QColor(255, 255, 255, 235 if enabled else 90)
        pen = QPen(base_color)
        pen.setWidthF(1.7)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        rect = QRectF(self.rect()).adjusted(9, 9, -9, -9)
        cx = rect.center().x()
        cy = rect.center().y()
        w = rect.width()
        h = rect.height()

        name = self._icon_name

        if name == "back":
            path = QPainterPath()
            path.moveTo(cx + w * 0.24, cy - h * 0.34)
            path.lineTo(cx - w * 0.20, cy)
            path.lineTo(cx + w * 0.24, cy + h * 0.34)
            painter.drawPath(path)

        elif name == "forward":
            path = QPainterPath()
            path.moveTo(cx - w * 0.24, cy - h * 0.34)
            path.lineTo(cx + w * 0.20, cy)
            path.lineTo(cx - w * 0.24, cy + h * 0.34)
            painter.drawPath(path)

        elif name == "reload":
            r = min(w, h) * 0.34
            arc_rect = QRectF(cx - r, cy - r, r * 2, r * 2)
            painter.drawArc(arc_rect, 40 * 16, 280 * 16)
            head = QPainterPath()
            ang_x = cx + r * 0.98
            ang_y = cy - r * 0.15
            head.moveTo(ang_x, ang_y)
            head.lineTo(ang_x + 4.5, ang_y - 3.5)
            head.lineTo(ang_x + 1.5, ang_y + 4.5)
            painter.setBrush(base_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(head)

        elif name == "home":
            path = QPainterPath()
            path.moveTo(cx - w * 0.32, cy + h * 0.06)
            path.lineTo(cx, cy - h * 0.34)
            path.lineTo(cx + w * 0.32, cy + h * 0.06)
            painter.drawPath(path)
            painter.drawRect(QRectF(cx - w * 0.20, cy + h * 0.02, w * 0.40, h * 0.32))

        elif name == "settings":
            r_outer = min(w, h) * 0.30
            r_inner = r_outer * 0.42
            painter.drawEllipse(QPointF(cx, cy), r_outer, r_outer)
            painter.drawEllipse(QPointF(cx, cy), r_inner, r_inner)
            for i in range(6):
                angle = math.radians(i * 60)
                x1 = cx + math.cos(angle) * (r_outer + 1)
                y1 = cy + math.sin(angle) * (r_outer + 1)
                x2 = cx + math.cos(angle) * (r_outer + 4.5)
                y2 = cy + math.sin(angle) * (r_outer + 4.5)
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        elif name == "find":
            r = min(w, h) * 0.28
            offset_x = cx - w * 0.06
            offset_y = cy - h * 0.06
            painter.drawEllipse(QPointF(offset_x, offset_y), r, r)
            painter.drawLine(
                QPointF(offset_x + r * 0.7, offset_y + r * 0.7),
                QPointF(cx + w * 0.30, cy + h * 0.30),
            )

        elif name == "minimize":
            painter.drawLine(QPointF(cx - w * 0.28, cy), QPointF(cx + w * 0.28, cy))

        elif name == "maximize":
            painter.drawRect(QRectF(cx - w * 0.22, cy - h * 0.22, w * 0.44, h * 0.44))

        elif name == "restore":
            painter.drawRect(QRectF(cx - w * 0.26, cy - h * 0.14, w * 0.34, h * 0.34))
            painter.drawRect(QRectF(cx - w * 0.10, cy - h * 0.28, w * 0.34, h * 0.34))

        elif name == "close":
            painter.drawLine(QPointF(cx - w * 0.26, cy - h * 0.26), QPointF(cx + w * 0.26, cy + h * 0.26))
            painter.drawLine(QPointF(cx + w * 0.26, cy - h * 0.26), QPointF(cx - w * 0.26, cy + h * 0.26))

        painter.end()


__all__ = ["IconButton"]