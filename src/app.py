"""
Application setup and entry point helper.
Creates QApplication, initializes i18n, and shows the main window.
"""

import sys

from PyQt6.QtWidgets import QApplication

from src.i18n import I18nManager
from src.ui.main_window import MainWindow


def run():
    """Initialize and run the application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Consistent cross-platform look

    # Initialize i18n with Vietnamese as default
    i18n = I18nManager(default_lang="vi")

    # Create and show main window
    window = MainWindow(i18n)
    window.show()

    sys.exit(app.exec())
