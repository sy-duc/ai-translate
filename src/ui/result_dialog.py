"""
Result dialog shown after translation completes.
Shows lists of successful and failed files.
"""

import os
import subprocess
import sys

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QPushButton, QGroupBox,
)
from PyQt6.QtCore import Qt

from src.i18n import I18nManager


class ResultDialog(QDialog):
    """Dialog displaying translation results: successes and errors."""

    def __init__(
        self,
        i18n: I18nManager,
        success_files: list[tuple[str, str]],  # (original_name, output_path)
        error_files: list[tuple[str, str]],     # (original_name, error_message)
        parent=None,
    ):
        super().__init__(parent)
        self._i18n = i18n
        self._success_files = success_files
        self._error_files = error_files
        # Collect unique output directories for "Open folder" button
        self._output_dirs: set[str] = set()
        for _, path in success_files:
            if path:
                self._output_dirs.add(os.path.dirname(path))

        self._init_ui()

    def _init_ui(self):
        """Build the result dialog UI."""
        t = self._i18n.t
        self.setWindowTitle(t("result_title"))
        self.setMinimumWidth(450)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout(self)

        # --- Success list ---
        if self._success_files:
            success_group = QGroupBox(f"{t('result_success')} ({len(self._success_files)})")
            success_layout = QVBoxLayout()
            success_list = QListWidget()
            for original_name, output_path in self._success_files:
                output_name = os.path.basename(output_path) if output_path else original_name
                success_list.addItem(f"{original_name}  ->  {output_name}")
            success_list.setMaximumHeight(150)
            success_layout.addWidget(success_list)
            success_group.setLayout(success_layout)
            main_layout.addWidget(success_group)

        # --- Error list ---
        if self._error_files:
            error_group = QGroupBox(f"{t('result_error')} ({len(self._error_files)})")
            error_layout = QVBoxLayout()
            error_list = QListWidget()
            for original_name, error_msg in self._error_files:
                error_list.addItem(f"{original_name}  -  {error_msg}")
            error_list.setMaximumHeight(150)
            error_layout.addWidget(error_list)
            error_group.setLayout(error_layout)
            main_layout.addWidget(error_group)

        # --- Bottom buttons ---
        btn_layout = QHBoxLayout()

        if self._output_dirs:
            open_folder_btn = QPushButton(t("result_open_folder"))
            open_folder_btn.clicked.connect(self._on_open_folder)
            btn_layout.addWidget(open_folder_btn)

        btn_layout.addStretch()

        close_btn = QPushButton(t("result_close"))
        close_btn.setDefault(True)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        main_layout.addLayout(btn_layout)

    def _on_open_folder(self):
        """Open the first output directory in the system file manager."""
        if not self._output_dirs:
            return
        dir_path = next(iter(self._output_dirs))
        # Cross-platform open folder
        if sys.platform == "win32":
            os.startfile(dir_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", dir_path])
        else:
            subprocess.Popen(["xdg-open", dir_path])
