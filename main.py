from __future__ import annotations

import os

os.environ.setdefault(
    "QTWEBENGINE_CHROMIUM_FLAGS",
    "--disable-checker-imaging --disable-features=CalculateNativeWinOcclusion"
)

import sys
import logging
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

try:
    from app.window import AcrylicBackgroundBrowser
except Exception as e:
    logger.exception("Failed to import AcrylicBackgroundBrowser: %s", e)
    raise

try:
    import gbrowser_native
    logger.info("Native module loaded: gbrowser_native")
except Exception:
    logger.info("Native module not available, using Python fallback for system effects")


def load_styles(qss_path: Path) -> None:
    if not qss_path.exists():
        logger.info("Stylesheet not found: %s", qss_path)
        return
    try:
        qss = qss_path.read_text(encoding="utf-8")
        QApplication.instance().setStyleSheet(qss)
        logger.info("Stylesheet loaded: %s", qss_path)
    except Exception:
        logger.exception("Error loading stylesheet: %s", qss_path)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("GBrowser")
    app.setApplicationVersion("3.0.2-alpha3")
    app.setOrganizationName("gbrowser")
    app.setFont(QFont("Segoe UI", 10))

    project_root = Path(__file__).resolve().parent
    load_styles(project_root / "ui" / "styles.qss")

    try:
        w = AcrylicBackgroundBrowser()
    except Exception:
        logger.exception("Error creating main window")
        raise

    w.show()

    try:
        return app.exec()
    except Exception:
        logger.exception("Error in main loop")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
