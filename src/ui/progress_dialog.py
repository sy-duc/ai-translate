"""
Progress dialog shown during translation.
Displays per-file status and overall progress bar.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QProgressBar, QPushButton, QListWidget,
)
from PyQt6.QtCore import Qt

from src.i18n import I18nManager


class ProgressDialog(QDialog):
    """Modal dialog showing translation progress."""

    def __init__(self, i18n: I18nManager, file_names: list[str], parent=None):
        super().__init__(parent)
        self._i18n = i18n
        self._file_names = file_names
        self._cancelled = False

        self._init_ui()

    def _init_ui(self):
        """Build the progress dialog UI."""
        t = self._i18n.t
        self.setWindowTitle(t("progress_title"))
        self.setMinimumWidth(400)
        self.setModal(True)
        # Prevent closing via X button during translation
        self.setWindowFlags(
            self.windowFlags()
            & ~Qt.WindowType.WindowCloseButtonHint
            & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        main_layout = QVBoxLayout(self)

        # Current file label
        self._current_file_label = QLabel(t("progress_file", filename="..."))
        main_layout.addWidget(self._current_file_label)

        # Per-file progress bar
        self._file_progress = QProgressBar()
        self._file_progress.setRange(0, 100)
        self._file_progress.setValue(0)
        main_layout.addWidget(self._file_progress)

        # File status list (shows completed files with status)
        self._file_list = QListWidget()
        self._file_list.setMaximumHeight(120)
        main_layout.addWidget(self._file_list)

        # Overall progress label + bar
        self._overall_label = QLabel(t("progress_overall"))
        main_layout.addWidget(self._overall_label)

        self._overall_progress = QProgressBar()
        self._overall_progress.setRange(0, len(self._file_names))
        self._overall_progress.setValue(0)
        main_layout.addWidget(self._overall_progress)

        # Cancel button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self._cancel_btn = QPushButton(t("progress_cancel"))
        self._cancel_btn.clicked.connect(self._on_cancel)
        btn_layout.addWidget(self._cancel_btn)
        main_layout.addLayout(btn_layout)

    # --- Public API for orchestrator to update progress ---

    def set_current_file(self, filename: str):
        """Update the current file being translated."""
        self._current_file_label.setText(
            self._i18n.t("progress_file", filename=filename)
        )
        self._file_progress.setValue(0)

    def set_file_progress(self, percent: int):
        """Update per-file progress (0-100)."""
        self._file_progress.setValue(min(percent, 100))

    def mark_file_done(self, filename: str, success: bool, error_msg: str = ""):
        """Mark a file as completed in the list."""
        if success:
            self._file_list.addItem(f"  {filename}")
        else:
            self._file_list.addItem(f"  {filename} - {error_msg}")
        # Update overall progress
        self._overall_progress.setValue(self._overall_progress.value() + 1)

    def is_cancelled(self) -> bool:
        """Check if user has requested cancellation."""
        return self._cancelled

    # --- Slots ---

    def _on_cancel(self):
        """Handle cancel button click."""
        self._cancelled = True
        self._cancel_btn.setEnabled(False)
        self._cancel_btn.setText("...")
