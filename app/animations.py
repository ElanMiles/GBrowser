from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QGraphicsDropShadowEffect


def fade_window(widget: QWidget, duration: int = 240, start: float = 0.0, end: float = 1.0) -> QPropertyAnimation:
    widget.setWindowOpacity(start)
    anim = QPropertyAnimation(widget, b"windowOpacity", widget)
    anim.setDuration(duration)
    anim.setStartValue(start)
    anim.setEndValue(end)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
    return anim


def slide_geometry(widget: QWidget, target: QRect, duration: int = 200) -> QPropertyAnimation:
    anim = QPropertyAnimation(widget, b"geometry", widget)
    anim.setDuration(duration)
    anim.setStartValue(widget.geometry())
    anim.setEndValue(target)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
    return anim


def install_hover_glow(widget: QWidget, color: QColor = None, max_blur: float = 16.0) -> None:
    if color is None:
        color = QColor(90, 130, 255)

    effect = QGraphicsDropShadowEffect(widget)
    effect.setColor(color)
    effect.setOffset(0, 0)
    effect.setBlurRadius(0)
    widget.setGraphicsEffect(effect)

    anim_in = QPropertyAnimation(effect, b"blurRadius", widget)
    anim_in.setDuration(150)
    anim_in.setEndValue(max_blur)

    anim_out = QPropertyAnimation(effect, b"blurRadius", widget)
    anim_out.setDuration(150)
    anim_out.setEndValue(0.0)

    original_enter = widget.enterEvent
    original_leave = widget.leaveEvent

    def on_enter(event):
        anim_out.stop()
        anim_in.setStartValue(effect.blurRadius())
        anim_in.start()
        original_enter(event)

    def on_leave(event):
        anim_in.stop()
        anim_out.setStartValue(effect.blurRadius())
        anim_out.start()
        original_leave(event)

    widget.enterEvent = on_enter
    widget.leaveEvent = on_leave


__all__ = ["fade_window", "slide_geometry", "install_hover_glow"]