"""
Settings dialog for configuring API keys, output directory, and offline model.
Opened via the gear icon button on the main window title bar.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QRadioButton,
    QFileDialog, QFormLayout, QMessageBox, QButtonGroup,
)
from PyQt6.QtCore import Qt

from src.constants import ENGINES
from src.i18n import I18nManager


class SettingsDialog(QDialog):
    """Dialog to configure API keys, output directory, and offline model."""

    def __init__(self, i18n: I18nManager, parent=None):
        super().__init__(parent)
        self._i18n = i18n
        # Store current settings (will be connected to data layer later)
        self._api_keys: dict[str, str] = {}
        self._output_dir: str = ""
        self._output_same_as_source: bool = True

        self._init_ui()

    def _init_ui(self):
        """Build the settings dialog UI."""
        t = self._i18n.t
        self.setWindowTitle(t("settings_title"))
        self.setMinimumWidth(480)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout(self)

        # --- API Keys group ---
        api_group = QGroupBox(t("settings_api_keys"))
        api_layout = QFormLayout()

        self._key_inputs: dict[str, QLineEdit] = {}
        self._test_buttons: dict[str, QPushButton] = {}

        for engine_key, i18n_key, requires_key in ENGINES:
            if not requires_key:
                continue  # Skip offline engine
            row_layout = QHBoxLayout()
            # API key input field (masked)
            key_input = QLineEdit()
            key_input.setPlaceholderText(f"sk-... / API key")
            key_input.setEchoMode(QLineEdit.EchoMode.Password)
            row_layout.addWidget(key_input, stretch=1)
            # Test button to validate the key
            test_btn = QPushButton(t("settings_test_key"))
            test_btn.setFixedWidth(80)
            test_btn.clicked.connect(lambda checked, k=engine_key: self._on_test_key(k))
            row_layout.addWidget(test_btn)

            api_layout.addRow(t(i18n_key) + ":", row_layout)
            self._key_inputs[engine_key] = key_input
            self._test_buttons[engine_key] = test_btn

        api_group.setLayout(api_layout)
        main_layout.addWidget(api_group)

        # --- Output directory group ---
        output_group = QGroupBox(t("settings_output_dir"))
        output_layout = QVBoxLayout()

        # Radio: same as source
        self._radio_same = QRadioButton(t("settings_output_same"))
        self._radio_same.setChecked(True)
        output_layout.addWidget(self._radio_same)

        # Radio: custom directory + browse
        custom_row = QHBoxLayout()
        self._radio_custom = QRadioButton(t("settings_output_custom"))
        custom_row.addWidget(self._radio_custom)

        self._output_dir_input = QLineEdit()
        self._output_dir_input.setEnabled(False)
        custom_row.addWidget(self._output_dir_input, stretch=1)

        self._browse_btn = QPushButton(t("settings_browse"))
        self._browse_btn.setFixedWidth(80)
        self._browse_btn.setEnabled(False)
        self._browse_btn.clicked.connect(self._on_browse_output)
        custom_row.addWidget(self._browse_btn)

        output_layout.addLayout(custom_row)

        # Group radios so only one can be selected
        output_radio_group = QButtonGroup(self)
        output_radio_group.addButton(self._radio_same)
        output_radio_group.addButton(self._radio_custom)

        # Enable/disable custom dir input based on radio selection
        self._radio_custom.toggled.connect(self._on_output_radio_changed)

        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)

        # --- Offline model group ---
        model_group = QGroupBox(t("settings_offline_model"))
        model_layout = QHBoxLayout()

        self._model_status_label = QLabel(
            f"{t('settings_model_status')} {t('settings_model_not_downloaded')}"
        )
        model_layout.addWidget(self._model_status_label, stretch=1)

        self._download_btn = QPushButton(t("settings_download_model"))
        self._download_btn.clicked.connect(self._on_download_model)
        model_layout.addWidget(self._download_btn)

        model_group.setLayout(model_layout)
        main_layout.addWidget(model_group)

        # --- Bottom buttons (Save / Cancel) ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton(t("settings_save"))
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton(t("settings_cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        main_layout.addLayout(btn_layout)

    # --- Slots ---

    def _on_output_radio_changed(self, checked: bool):
        """Enable custom directory input when custom radio is selected."""
        self._output_dir_input.setEnabled(checked)
        self._browse_btn.setEnabled(checked)

    def _on_browse_output(self):
        """Open folder picker for custom output directory."""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            self._i18n.t("settings_output_dir"),
        )
        if dir_path:
            self._output_dir_input.setText(dir_path)

    def _on_test_key(self, engine_key: str):
        """Test the API key for a given engine. (Stub - business logic later)"""
        key_value = self._key_inputs[engine_key].text().strip()
        if not key_value:
            QMessageBox.warning(
                self,
                self._i18n.t("warning"),
                f"Please enter an API key for {engine_key}.",
            )
            return
        # TODO: Call engine.validate_api_key(key_value) and show result
        QMessageBox.information(
            self,
            self._i18n.t("confirm"),
            self._i18n.t("settings_test_not_implemented", engine=engine_key),
        )

    def _on_download_model(self):
        """Download offline translation model. (Stub - business logic later)"""
        # TODO: Trigger model download in background
        QMessageBox.information(
            self,
            self._i18n.t("settings_offline_model"),
            self._i18n.t("settings_download_not_implemented"),
        )

    def _on_save(self):
        """Save settings and close dialog. (Stub - data layer later)"""
        # Collect API keys
        for engine_key, key_input in self._key_inputs.items():
            self._api_keys[engine_key] = key_input.text().strip()

        # Collect output dir config
        self._output_same_as_source = self._radio_same.isChecked()
        self._output_dir = self._output_dir_input.text().strip()

        # TODO: Persist to SQLite via settings_repo
        self.accept()

    # --- Public API for loading/getting settings ---

    def load_settings(self, api_keys: dict[str, str], output_dir: str, output_same: bool):
        """Load existing settings into the dialog fields."""
        for engine_key, value in api_keys.items():
            if engine_key in self._key_inputs:
                self._key_inputs[engine_key].setText(value)
        self._radio_same.setChecked(output_same)
        self._radio_custom.setChecked(not output_same)
        self._output_dir_input.setText(output_dir)

    def get_api_keys(self) -> dict[str, str]:
        """Return configured API keys."""
        return dict(self._api_keys)

    def get_output_config(self) -> tuple[bool, str]:
        """Return (same_as_source, custom_output_dir)."""
        return self._output_same_as_source, self._output_dir
