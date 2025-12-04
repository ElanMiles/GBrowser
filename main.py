from __future__ import annotations

import sys
import logging
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

try:
    from app.window import AcrylicBackgroundBrowser
except Exception as e:
    logger.exception("Failed to import AcrylicBackgroundBrowser from app.window: %s", e)
    raise


def load_styles(qss_path: Path) -> None:
    if not qss_path.exists():
        logger.info("Stylesheet file not found: %s", qss_path)
        return

    try:
        qss = qss_path.read_text(encoding="utf-8")
        QApplication.instance().setStyleSheet(qss)
        logger.info("Stylesheet Loaded: %s", qss_path)
    except Exception:
        logger.exception("Error loading QSS: %s", qss_path)


def main() -> int:
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setApplicationName("GBrowser")
    app.setOrganizationName("gbrowser")

    app.setFont(QFont("Segoe UI", 10))

    project_root = Path(__file__).resolve().parent
    styles_path = project_root / "ui" / "styles.qss"
    load_styles(styles_path)

    try:
        w = AcrylicBackgroundBrowser()
    except Exception:
        logger.exception("Error creating the main window")
        raise

    w.show()

    try:
        return app.exec()
    except Exception:
        logger.exception("Error in the main loop")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
