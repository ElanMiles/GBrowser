from __future__ import annotations

import logging
import time
from typing import Optional
from urllib.parse import urlparse

from PySide6.QtCore import QObject, QTimer

logger = logging.getLogger(__name__)

try:
    import gbrowser_native as _native
    _NATIVE_AVAILABLE = True
except Exception:
    _native = None
    _NATIVE_AVAILABLE = False

DEFAULT_CLIENT_ID = "1288842332489728000"


class DiscordPresenceManager(QObject):

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._client: Optional[object] = None
        self._enabled = False
        self._connected = False
        self._start_time = int(time.time())
        self._reconnect_timer = QTimer(self)
        self._reconnect_timer.setInterval(15000)
        self._reconnect_timer.timeout.connect(self._try_reconnect)

    def is_available(self) -> bool:
        return _NATIVE_AVAILABLE

    def is_connected(self) -> bool:
        return self._connected

    def enable(self, client_id: str = DEFAULT_CLIENT_ID) -> None:
        self._enabled = True
        if not _NATIVE_AVAILABLE:
            logger.info("Discord RPC native module unavailable")
            return
        try:
            self._client = _native.DiscordRPC()
            self._connected = bool(self._client.connect(client_id))
            if self._connected:
                self._start_time = int(time.time())
                self._reconnect_timer.stop()
            else:
                self._reconnect_timer.start()
        except Exception:
            logger.exception("Failed to initialize Discord RPC")
            self._connected = False
            self._reconnect_timer.start()

    def disable(self) -> None:
        self._enabled = False
        self._reconnect_timer.stop()
        if self._client is not None:
            try:
                self._client.disconnect()
            except Exception:
                pass
        self._client = None
        self._connected = False

    def _try_reconnect(self) -> None:
        if not self._enabled or self._connected or not _NATIVE_AVAILABLE:
            return
        try:
            if self._client is None:
                self._client = _native.DiscordRPC()
            self._connected = bool(self._client.connect(DEFAULT_CLIENT_ID))
            if self._connected:
                self._start_time = int(time.time())
                self._reconnect_timer.stop()
        except Exception:
            self._connected = False

    def update_browsing(self, title: str, url: str) -> None:
        if not self._enabled or not self._connected or self._client is None:
            return
        try:
            domain = urlparse(url).netloc or "GBrowser"
            details = title[:110] if title else "Browsing the web"
            state = domain[:110]
            self._client.update_presence(
                state,
                details,
                self._start_time,
                "gbrowser_logo",
                "GBrowser Alpha 3",
                "",
                "",
            )
        except Exception:
            logger.exception("Failed to update Discord presence")
            self._connected = False
            self._reconnect_timer.start()

    def clear(self) -> None:
        if self._client is not None and self._connected:
            try:
                self._client.clear_presence()
            except Exception:
                pass


__all__ = ["DiscordPresenceManager", "DEFAULT_CLIENT_ID"]