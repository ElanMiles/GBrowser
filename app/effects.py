from __future__ import annotations

import ctypes
import sys
import platform
from ctypes import wintypes
from typing import Optional


ACCENT_DISABLED = 0
ACCENT_ENABLE_GRADIENT = 1
ACCENT_ENABLE_TRANSPARENTGRADIENT = 2
ACCENT_ENABLE_BLURBEHIND = 3
ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
ACCENT_INVALID_STATE = 5

# WINDOWCOMPOSITIONATTRIB
WCA_ACCENT_POLICY = 19


class ACCENT_POLICY(ctypes.Structure):
    _fields_ = [
        ("AccentState", ctypes.c_int),
        ("AccentFlags", ctypes.c_int),
        ("GradientColor", ctypes.c_uint32),
        ("AnimationId", ctypes.c_int),
    ]


class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
    _fields_ = [
        ("Attribute", ctypes.c_int),
        ("Data", ctypes.c_void_p),
        ("SizeOfData", ctypes.c_size_t),
    ]



def is_windows() -> bool:
    return platform.system().lower() == "windows"


def _get_set_window_composition_attribute():
    if not is_windows():
        return None
    try:
        user32 = ctypes.windll.user32
        func = getattr(user32, "SetWindowCompositionAttribute", None)
        if not func:
            return None
        func.argtypes = [wintypes.HWND, ctypes.POINTER(WINDOWCOMPOSITIONATTRIBDATA)]
        func.restype = wintypes.BOOL
        return func
    except Exception:
        return None


def hwnd_of(widget) -> Optional[int]:
    if not is_windows():
        return None
    try:
        return int(widget.winId())
    except Exception:
        return None



def enable_acrylic(hwnd: int, color: int = 0x661F2937) -> bool:
    if not is_windows():
        return False

    func = _get_set_window_composition_attribute()
    if func is None:
        return False

    try:
        accent = ACCENT_POLICY()
        accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
        accent.AccentFlags = 2
        accent.GradientColor = ctypes.c_uint32(color)

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = WCA_ACCENT_POLICY
        data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.c_void_p)
        data.SizeOfData = ctypes.sizeof(accent)

        res = func(wintypes.HWND(hwnd), ctypes.byref(data))
        return bool(res)
    except Exception:
        return False


def remove_acrylic(hwnd: int) -> bool:
    if not is_windows():
        return False
    func = _get_set_window_composition_attribute()
    if func is None:
        return False
    try:
        accent = ACCENT_POLICY()
        accent.AccentState = ACCENT_DISABLED
        accent.AccentFlags = 0
        accent.GradientColor = 0
        accent.AnimationId = 0

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = WCA_ACCENT_POLICY
        data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.c_void_p)
        data.SizeOfData = ctypes.sizeof(accent)

        res = func(wintypes.HWND(hwnd), ctypes.byref(data))
        return bool(res)
    except Exception:
        return False


def apply_acrylic_to_widget(widget, color: int = 0x661F2937) -> bool:
    hwnd = hwnd_of(widget)
    if hwnd is None:
        return False
    return enable_acrylic(hwnd, color)



def enable_blur_behind(hwnd: int, color: int = 0x00000000) -> bool:
    if not is_windows():
        return False
    func = _get_set_window_composition_attribute()
    if func is None:
        return False
    try:
        accent = ACCENT_POLICY()
        accent.AccentState = ACCENT_ENABLE_BLURBEHIND
        accent.AccentFlags = 0
        accent.GradientColor = ctypes.c_uint32(color)
        accent.AnimationId = 0

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = WCA_ACCENT_POLICY
        data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.c_void_p)
        data.SizeOfData = ctypes.sizeof(accent)

        res = func(wintypes.HWND(hwnd), ctypes.byref(data))
        return bool(res)
    except Exception:
        return False


if __name__ == "__main__":
    print("app.effects - a module with acrylic functions. Import it into your GUI code and use it.:")
    print("  from app.effects import apply_acrylic_to_widget, enable_acrylic")
    print("  apply_acrylic_to_widget(window, color=0x661F2937)")
