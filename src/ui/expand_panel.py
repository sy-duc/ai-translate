"""
Expandable panel for advanced options.
Contains: document domain (checkboxes), translation style (radio),
and translation engine (radio).
Shown/hidden when user clicks "Expand >>" / "<< Collapse".
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QCheckBox, QRadioButton, QButtonGroup, QLabel,
    QFrame, QGridLayout,
)

from src.constants import DOMAINS, STYLES, ENGINES
from src.i18n import I18nManager


class ExpandPanel(QWidget):
    """Collapsible panel containing advanced translation options."""

    def __init__(self, i18n: I18nManager, parent=None):
        super().__init__(parent)
        self._i18n = i18n

        # State storage
        self._domain_checkboxes: dict[str, QCheckBox] = {}
        self._style_radios: dict[str, QRadioButton] = {}
        self._engine_radios: dict[str, QRadioButton] = {}

        self._init_ui()

    def _init_ui(self):
        """Build the expand panel UI with 3 sections."""
        t = self._i18n.t
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Separator line at the top
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)

        # Group box for all advanced options
        self._group = QGroupBox(t("advanced_group"))
        group_layout = QVBoxLayout()

        # --- Section 1: Document domain (checkboxes, multi-select) ---
        self._domain_label = QLabel(t("domain_label"))
        group_layout.addWidget(self._domain_label)
        domain_layout = QHBoxLayout()
        # Arrange checkboxes in a flow layout (2 rows)
        domain_left = QVBoxLayout()
        domain_right = QVBoxLayout()

        for i, (key, i18n_key, default_checked) in enumerate(DOMAINS):
            cb = QCheckBox(t(i18n_key))
            cb.setChecked(default_checked)
            self._domain_checkboxes[key] = cb
            # Split into 2 columns
            if i < len(DOMAINS) // 2 + len(DOMAINS) % 2:
                domain_left.addWidget(cb)
            else:
                domain_right.addWidget(cb)

        domain_layout.addLayout(domain_left)
        domain_layout.addLayout(domain_right)
        group_layout.addLayout(domain_layout)

        group_layout.addSpacing(8)

        # --- Section 2: Translation style (radio, single-select) ---
        self._style_label = QLabel(t("style_label"))
        group_layout.addWidget(self._style_label)
        style_grid = QGridLayout()
        style_grid.setColumnStretch(0, 1)
        style_grid.setColumnStretch(1, 1)
        style_grid.setColumnStretch(2, 1)
        style_btn_group = QButtonGroup(self)

        for i, (key, i18n_key) in enumerate(STYLES):
            radio = QRadioButton(t(i18n_key))
            if key == "default":
                radio.setChecked(True)
            style_btn_group.addButton(radio)
            self._style_radios[key] = radio
            style_grid.addWidget(radio, i // 3, i % 3)

        group_layout.addLayout(style_grid)

        group_layout.addSpacing(8)

        # --- Section 3: Translation engine (radio, single-select) ---
        self._engine_label = QLabel(t("engine_label"))
        group_layout.addWidget(self._engine_label)
        engine_grid = QGridLayout()
        engine_grid.setColumnStretch(0, 1)
        engine_grid.setColumnStretch(1, 1)
        engine_grid.setColumnStretch(2, 1)
        engine_btn_group = QButtonGroup(self)

        for i, (key, i18n_key, _) in enumerate(ENGINES):
            radio = QRadioButton(t(i18n_key))
            if key == "offline":
                radio.setChecked(True)
            engine_btn_group.addButton(radio)
            self._engine_radios[key] = radio
            engine_grid.addWidget(radio, i // 3, i % 3)

        group_layout.addLayout(engine_grid)

        self._group.setLayout(group_layout)
        main_layout.addWidget(self._group)

    # --- Public API to get current selections ---

    def get_selected_domains(self) -> list[str]:
        """Return list of checked domain keys."""
        return [key for key, cb in self._domain_checkboxes.items() if cb.isChecked()]

    def get_selected_style(self) -> str:
        """Return the selected style key."""
        for key, radio in self._style_radios.items():
            if radio.isChecked():
                return key
        return "default"

    def get_selected_engine(self) -> str:
        """Return the selected engine key."""
        for key, radio in self._engine_radios.items():
            if radio.isChecked():
                return key
        return "offline"

    def retranslate_ui(self):
        """Update all labels when UI language changes."""
        t = self._i18n.t
        self._group.setTitle(t("advanced_group"))
        self._domain_label.setText(t("domain_label"))
        self._style_label.setText(t("style_label"))
        self._engine_label.setText(t("engine_label"))
        for key, i18n_key, _ in DOMAINS:
            if key in self._domain_checkboxes:
                self._domain_checkboxes[key].setText(t(i18n_key))
        for key, i18n_key in STYLES:
            if key in self._style_radios:
                self._style_radios[key].setText(t(i18n_key))
        for key, i18n_key, _ in ENGINES:
            if key in self._engine_radios:
                self._engine_radios[key].setText(t(i18n_key))
