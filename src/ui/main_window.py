"""
Main window - UniKey-style compact UI.
Layout:
  - Title bar with Settings gear icon
  - Control panel (left: labels/dropdowns, right: buttons)
  - Expandable advanced options panel (hidden by default)
  - Bottom buttons: Guide, Info, Glossary
"""

import os

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QComboBox, QListWidget, QPushButton, QFileDialog,
    QMessageBox, QSizePolicy, QToolButton, QStyle,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

from src.constants import UI_LANGUAGES, TARGET_LANGUAGES, ENGINES
from src.i18n import I18nManager
from src.ui.expand_panel import ExpandPanel
from src.ui.settings_dialog import SettingsDialog
from src.ui.glossary_dialog import GlossaryDialog
from src.ui.progress_dialog import ProgressDialog
from src.ui.result_dialog import ResultDialog
from src.ui.info_dialog import InfoDialog
from src.ui.guide_dialog import GuideDialog


class MainWindow(QMainWindow):
    """Main application window with UniKey-like compact layout."""

    # Fixed window dimensions (compact like UniKey)
    COLLAPSED_WIDTH = 480
    COLLAPSED_HEIGHT = 320
    EXPANDED_HEIGHT = 560

    def __init__(self, i18n: I18nManager):
        super().__init__()
        self._i18n = i18n

        # State
        self._is_expanded = False
        self._selected_files: list[str] = []  # Full paths of selected files
        self._glossary_entries: list[tuple[str, str, str, str]] = []
        self._api_keys: dict[str, str] = {}
        self._output_same_as_source = True
        self._output_dir = ""

        self._init_ui()
        self._apply_compact_size()

    def _init_ui(self):
        """Build the entire main window UI."""
        t = self._i18n.t
        self.setWindowTitle(t("app_title"))
        # Fixed size, not resizable (like UniKey)
        self.setFixedSize(self.COLLAPSED_WIDTH, self.COLLAPSED_HEIGHT)
        # Remove maximize button
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowMinimizeButtonHint
        )

        # --- Central widget ---
        central = QWidget()
        self.setCentralWidget(central)
        self._main_layout = QVBoxLayout(central)
        self._main_layout.setSpacing(6)
        self._main_layout.setContentsMargins(8, 8, 8, 8)

        # --- Control group (main content area) ---
        control_group = QGroupBox()
        # Header row: group title + settings gear button
        header_row = QHBoxLayout()
        self._control_label = QLabel(f"<b>{t('control_group')}</b>")
        header_row.addWidget(self._control_label)
        header_row.addStretch()
        self._settings_btn = QToolButton()
        self._settings_btn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        )
        self._settings_btn.setText("\u2699")
        self._settings_btn.setToolTip(t("settings_title"))
        self._settings_btn.setFixedSize(28, 28)
        self._settings_btn.clicked.connect(self._on_settings)
        header_row.addWidget(self._settings_btn)

        control_outer_layout = QVBoxLayout()
        control_outer_layout.addLayout(header_row)

        control_layout = QHBoxLayout()

        # LEFT side: labels and dropdowns
        left_layout = QVBoxLayout()

        # Interface language dropdown
        lang_row = QHBoxLayout()
        self._interface_label = QLabel(t("interface_label"))
        lang_row.addWidget(self._interface_label)
        self._ui_lang_combo = QComboBox()
        for code, name in UI_LANGUAGES:
            self._ui_lang_combo.addItem(name, code)
        # Set current to match i18n
        for i, (code, _) in enumerate(UI_LANGUAGES):
            if code == self._i18n.current_language:
                self._ui_lang_combo.setCurrentIndex(i)
                break
        self._ui_lang_combo.currentIndexChanged.connect(self._on_ui_language_changed)
        lang_row.addWidget(self._ui_lang_combo, stretch=1)
        left_layout.addLayout(lang_row)

        # File list label
        self._files_label = QLabel(t("files_label"))
        left_layout.addWidget(self._files_label)

        # File list (shows only file names, not paths)
        self._file_list = QListWidget()
        self._file_list.setMaximumHeight(100)
        self._file_list.setAlternatingRowColors(True)
        # Placeholder when empty
        self._update_file_list_placeholder()
        left_layout.addWidget(self._file_list, stretch=1)

        # Target language dropdown
        target_row = QHBoxLayout()
        self._target_label = QLabel(t("target_lang_label"))
        target_row.addWidget(self._target_label)
        self._target_lang_combo = QComboBox()
        for code, name in TARGET_LANGUAGES:
            self._target_lang_combo.addItem(name, code)
        target_row.addWidget(self._target_lang_combo, stretch=1)
        left_layout.addLayout(target_row)

        control_layout.addLayout(left_layout, stretch=1)

        # RIGHT side: action buttons
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Choose file button
        self._choose_btn = QPushButton(t("btn_choose_file"))
        self._choose_btn.setMinimumWidth(120)
        self._choose_btn.clicked.connect(self._on_choose_files)
        right_layout.addWidget(self._choose_btn)

        # Clear file list button
        self._clear_btn = QPushButton(t("btn_clear_files"))
        self._clear_btn.setMinimumWidth(120)
        self._clear_btn.clicked.connect(self._on_clear_files)
        right_layout.addWidget(self._clear_btn)

        # Translate button (hidden until files are selected)
        self._translate_btn = QPushButton(t("btn_translate"))
        self._translate_btn.setMinimumWidth(120)
        self._translate_btn.setStyleSheet("font-weight: bold;")
        self._translate_btn.clicked.connect(self._on_translate)
        self._translate_btn.setVisible(False)
        right_layout.addWidget(self._translate_btn)

        # Expand/Collapse button
        self._expand_btn = QPushButton(t("btn_expand"))
        self._expand_btn.setMinimumWidth(120)
        self._expand_btn.clicked.connect(self._on_toggle_expand)
        right_layout.addWidget(self._expand_btn)

        right_layout.addStretch()
        control_layout.addLayout(right_layout)

        control_outer_layout.addLayout(control_layout)
        control_group.setLayout(control_outer_layout)
        self._main_layout.addWidget(control_group)

        # --- Expand panel (hidden by default) ---
        self._expand_panel = ExpandPanel(self._i18n)
        self._expand_panel.setVisible(False)
        self._main_layout.addWidget(self._expand_panel)

        # --- Bottom buttons ---
        bottom_layout = QHBoxLayout()

        self._guide_btn = QPushButton(t("btn_guide"))
        self._guide_btn.clicked.connect(self._on_guide)
        bottom_layout.addWidget(self._guide_btn)

        self._info_btn = QPushButton(t("btn_info"))
        self._info_btn.clicked.connect(self._on_info)
        bottom_layout.addWidget(self._info_btn)

        self._glossary_btn = QPushButton(t("btn_glossary"))
        self._glossary_btn.clicked.connect(self._on_glossary)
        bottom_layout.addWidget(self._glossary_btn)

        self._main_layout.addLayout(bottom_layout)

    # --- Size management ---

    def _apply_compact_size(self):
        """Set window to collapsed size."""
        self.setFixedSize(self.COLLAPSED_WIDTH, self.COLLAPSED_HEIGHT)

    def _apply_expanded_size(self):
        """Set window to expanded size."""
        self.setFixedSize(self.COLLAPSED_WIDTH, self.EXPANDED_HEIGHT)

    # --- File list helpers ---

    def _update_file_list_placeholder(self):
        """Show placeholder text when no files are selected."""
        self._file_list.clear()
        if not self._selected_files:
            self._file_list.addItem(self._i18n.t("no_files"))
            self._file_list.item(0).setForeground(Qt.GlobalColor.gray)
            self._file_list.item(0).setFlags(Qt.ItemFlag.NoItemFlags)

    def _refresh_file_list(self):
        """Refresh the file list display with current selected files."""
        self._file_list.clear()
        if not self._selected_files:
            self._update_file_list_placeholder()
            self._translate_btn.setVisible(False)
            return
        for file_path in self._selected_files:
            self._file_list.addItem(os.path.basename(file_path))
        self._translate_btn.setVisible(True)

    # --- Slots: Button actions ---

    def _on_choose_files(self):
        """Open file dialog to select multiple files."""
        t = self._i18n.t
        files, _ = QFileDialog.getOpenFileNames(
            self,
            t("file_dialog_title"),
            "",
            t("file_dialog_filter"),
        )
        if files:
            # Append to existing selection (avoid duplicates)
            existing_set = set(self._selected_files)
            for f in files:
                if f not in existing_set:
                    self._selected_files.append(f)
            self._refresh_file_list()

    def _on_clear_files(self):
        """Clear all selected files from the list."""
        self._selected_files.clear()
        self._refresh_file_list()

    def _on_translate(self):
        """Start translating all selected files. (Stub - business logic later)"""
        t = self._i18n.t

        # Validate: files selected?
        if not self._selected_files:
            QMessageBox.warning(self, t("warning"), t("no_files_selected"))
            return

        # Validate: if using cloud engine, check API key
        engine_key = self._expand_panel.get_selected_engine()
        requires_key = any(
            key == engine_key and req
            for key, _, req in ENGINES
        )
        if requires_key and not self._api_keys.get(engine_key):
            engine_name = next(
                (i18n_key for key, i18n_key, _ in ENGINES if key == engine_key),
                engine_key,
            )
            QMessageBox.warning(
                self, t("warning"),
                t("no_engine_key", engine=t(engine_name)),
            )
            return

        # Gather translation parameters
        target_lang = self._target_lang_combo.currentData()
        domains = self._expand_panel.get_selected_domains()
        style = self._expand_panel.get_selected_style()

        # Show progress dialog
        file_names = [os.path.basename(f) for f in self._selected_files]
        progress = ProgressDialog(self._i18n, file_names, parent=self)
        progress.show()

        # TODO: Connect to orchestrator.translate_files()
        # For now, simulate completion immediately
        progress.close()

        # Show result dialog (stub data)
        success_files = [(os.path.basename(f), f) for f in self._selected_files]
        error_files: list[tuple[str, str]] = []
        result_dialog = ResultDialog(self._i18n, success_files, error_files, parent=self)
        result_dialog.exec()

    def _on_toggle_expand(self):
        """Toggle the expand panel visibility."""
        t = self._i18n.t
        self._is_expanded = not self._is_expanded

        if self._is_expanded:
            self._expand_panel.setVisible(True)
            self._expand_btn.setText(t("btn_collapse"))
            self._apply_expanded_size()
        else:
            self._expand_panel.setVisible(False)
            self._expand_btn.setText(t("btn_expand"))
            self._apply_compact_size()

    def _on_settings(self):
        """Open settings dialog."""
        dialog = SettingsDialog(self._i18n, parent=self)
        dialog.load_settings(self._api_keys, self._output_dir, self._output_same_as_source)
        if dialog.exec() == SettingsDialog.DialogCode.Accepted:
            self._api_keys = dialog.get_api_keys()
            self._output_same_as_source, self._output_dir = dialog.get_output_config()

    def _on_guide(self):
        """Open the user guide dialog."""
        dialog = GuideDialog(self._i18n, parent=self)
        dialog.exec()

    def _on_info(self):
        """Open the about/info dialog."""
        dialog = InfoDialog(self._i18n, parent=self)
        dialog.exec()

    def _on_glossary(self):
        """Open the glossary management dialog."""
        dialog = GlossaryDialog(self._i18n, parent=self)
        dialog.set_entries(self._glossary_entries)
        if dialog.exec() == GlossaryDialog.DialogCode.Accepted:
            self._glossary_entries = dialog.get_entries()

    def _on_ui_language_changed(self, index: int):
        """Switch UI language and retranslate all labels."""
        lang_code = self._ui_lang_combo.itemData(index)
        if not lang_code or lang_code == self._i18n.current_language:
            return
        self._i18n.set_language(lang_code)
        self._retranslate_ui()

    # --- Retranslate all UI elements when language changes ---

    def _retranslate_ui(self):
        """Update all text labels to match the new language."""
        t = self._i18n.t

        self.setWindowTitle(t("app_title"))
        self._settings_btn.setToolTip(t("settings_title"))

        # Control group header label
        self._control_label.setText(f"<b>{t('control_group')}</b>")

        self._interface_label.setText(t("interface_label"))
        self._files_label.setText(t("files_label"))
        self._target_label.setText(t("target_lang_label"))

        # Buttons
        self._choose_btn.setText(t("btn_choose_file"))
        self._clear_btn.setText(t("btn_clear_files"))
        self._translate_btn.setText(t("btn_translate"))
        self._expand_btn.setText(t("btn_collapse") if self._is_expanded else t("btn_expand"))
        self._guide_btn.setText(t("btn_guide"))
        self._info_btn.setText(t("btn_info"))
        self._glossary_btn.setText(t("btn_glossary"))

        # Refresh file list placeholder
        if not self._selected_files:
            self._update_file_list_placeholder()

        # Retranslate expand panel
        self._expand_panel.retranslate_ui()
