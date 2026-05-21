"""Road Damage Assessment System — Desktop Application Entry Point.

Launch: python app.py
"""

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.ui.main_window import MainWindow
from src.utils.logging_setup import get_logger

logger = get_logger("app")


def main() -> int:
    """Application entry point."""
    # High DPI scaling (Qt 6 handles this automatically, but explicit for clarity)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Road Damage Assessment System")
    app.setOrganizationName("UTRAN-BIM-AI")

    # Set default font
    font = app.font()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    logger.info("Application started")

    exit_code = app.exec()

    logger.info(f"Application exited with code {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
