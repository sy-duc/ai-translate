"""
Info (About) dialog showing app version, author, and description.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

from src.constants import APP_NAME, APP_VERSION, APP_AUTHOR
from src.i18n import I18nManager


class InfoDialog(QDialog):
    """Simple 'About' dialog with version and author info."""

    def __init__(self, i18n: I18nManager, parent=None):
        super().__init__(parent)
        self._i18n = i18n
        self._init_ui()

    def _init_ui(self):
        t = self._i18n.t
        self.setWindowTitle(t("info_title"))
        self.setFixedSize(300, 180)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # App name (bold, larger)
        name_label = QLabel(APP_NAME)
        name_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        # Version
        version_label = QLabel(t("info_version", version=APP_VERSION))
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        # Author
        author_label = QLabel(t("info_author", author=APP_AUTHOR))
        author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(author_label)

        layout.addSpacing(8)

        # Description
        desc_label = QLabel(t("info_description"))
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
