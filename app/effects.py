from __future__ import annotations

import logging
import platform
from typing import Optional

logger = logging.getLogger(__name__)

_native = None
_native_available = False

try:
    import gbrowser_native as _native
    _native_available = True
except Exception:
    _native = None
    _native_available = False

DWMWCP_DEFAULT = 0
DWMWCP_DONOTROUND = 1
DWMWCP_ROUND = 2
DWMWCP_ROUNDSMALL = 3


def is_windows() -> bool:
    return platform.system().lower() == "windows"


def native_available() -> bool:
    return _native_available


def supports_modern_backdrop() -> bool:
    if not _native_available:
        return False
    try:
        return bool(_native.supports_modern_backdrop())
    except Exception:
        return False


def windows_build_number() -> int:
    if not _native_available:
        return 0
    try:
        return int(_native.get_windows_build_number())
    except Exception:
        return 0


def hwnd_of(widget) -> Optional[int]:
    if not is_windows():
        return None
    try:
        return int(widget.winId())
    except Exception:
        return None


def _fallback_enable_acrylic(hwnd: int, color: int) -> bool:
    import ctypes
    from ctypes import wintypes

    ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
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

    try:
        user32 = ctypes.windll.user32
        func = user32.SetWindowCompositionAttribute
        func.argtypes = [wintypes.HWND, ctypes.POINTER(WINDOWCOMPOSITIONATTRIBDATA)]
        func.restype = wintypes.BOOL

        accent = ACCENT_POLICY()
        accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
        accent.AccentFlags = 2
        accent.GradientColor = ctypes.c_uint32(color)

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = WCA_ACCENT_POLICY
        data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.c_void_p)
        data.SizeOfData = ctypes.sizeof(accent)

        return bool(func(wintypes.HWND(hwnd), ctypes.byref(data)))
    except Exception:
        logger.exception("Fallback acrylic failed")
        return False


def enable_acrylic(hwnd: int, color: int = 0x661F2937) -> bool:
    if not is_windows() or hwnd is None:
        return False
    if _native_available:
        try:
            return bool(_native.enable_acrylic(hwnd, color))
        except Exception:
            logger.exception("Native enable_acrylic failed, falling back")
    return _fallback_enable_acrylic(hwnd, color)


def remove_acrylic(hwnd: int) -> bool:
    if not is_windows() or hwnd is None:
        return False
    if _native_available:
        try:
            return bool(_native.remove_backdrop(hwnd))
        except Exception:
            logger.exception("Native remove_backdrop failed")
    return False


def set_dark_titlebar(hwnd: int, enabled: bool = True) -> bool:
    if not is_windows() or hwnd is None or not _native_available:
        return False
    try:
        return bool(_native.set_dark_titlebar(hwnd, enabled))
    except Exception:
        return False


def set_rounded_corners(hwnd: int, preference: int = DWMWCP_ROUND) -> bool:
    if not is_windows() or hwnd is None or not _native_available:
        return False
    try:
        return bool(_native.set_rounded_corners(hwnd, preference))
    except Exception:
        return False


def set_window_shadow(hwnd: int, enabled: bool = True) -> bool:
    if not is_windows() or hwnd is None or not _native_available:
        return False
    try:
        return bool(_native.set_window_shadow(hwnd, enabled))
    except Exception:
        return False


def apply_system_backdrop(widget, mode: str = "Acrylic") -> bool:
    hwnd = hwnd_of(widget)
    if hwnd is None:
        return False

    set_dark_titlebar(hwnd, True)
    set_rounded_corners(hwnd, DWMWCP_ROUND)

    if not (_native_available and supports_modern_backdrop()):
        return False

    try:
        backdrop_type = _native.BACKDROP_MICA if mode == "Mica" else _native.BACKDROP_ACRYLIC
        return bool(_native.set_system_backdrop(hwnd, backdrop_type))
    except Exception:
        logger.exception("Modern backdrop failed")
        return False


def remove_system_backdrop(widget) -> bool:
    hwnd = hwnd_of(widget)
    if hwnd is None:
        return False
    if _native_available and supports_modern_backdrop():
        try:
            return bool(_native.set_system_backdrop(hwnd, _native.BACKDROP_NONE))
        except Exception:
            return False
    return True


def apply_acrylic_to_widget(widget, color: int = 0x661F2937) -> bool:
    hwnd = hwnd_of(widget)
    if hwnd is None:
        return False
    ok = enable_acrylic(hwnd, color)
    set_dark_titlebar(hwnd, True)
    set_rounded_corners(hwnd, DWMWCP_ROUND)
    return ok


def apply_mica_to_widget(widget, dark: bool = True) -> bool:
    return apply_system_backdrop(widget, "Mica")


__all__ = [
    "apply_acrylic_to_widget",
    "apply_mica_to_widget",
    "apply_system_backdrop",
    "remove_system_backdrop",
    "enable_acrylic",
    "remove_acrylic",
    "set_dark_titlebar",
    "set_rounded_corners",
    "set_window_shadow",
    "hwnd_of",
    "is_windows",
    "native_available",
    "supports_modern_backdrop",
    "windows_build_number",
]