"""
Glossary management dialog.
Allows adding, editing, deleting, importing and exporting translation terms.
Terms are bidirectional: adding EN->VI auto-creates VI->EN.
"""

import csv
import os

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox, QAbstractItemView,
)
from PyQt6.QtCore import Qt

from src.constants import TARGET_LANGUAGES
from src.i18n import I18nManager


class GlossaryDialog(QDialog):
    """Dialog for managing the bidirectional glossary."""

    def __init__(self, i18n: I18nManager, parent=None):
        super().__init__(parent)
        self._i18n = i18n
        # In-memory glossary entries: list of (source_term, source_lang, target_term, target_lang)
        self._entries: list[tuple[str, str, str, str]] = []

        self._init_ui()

    def _init_ui(self):
        """Build the glossary dialog UI."""
        t = self._i18n.t
        self.setWindowTitle(t("glossary_title"))
        self.setMinimumSize(600, 480)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout(self)

        # --- Input area (add/update term) ---
        input_group = QGroupBox()
        input_layout = QVBoxLayout()

        # Row 1: Source language + source term
        row1 = QHBoxLayout()
        row1.addWidget(QLabel(t("glossary_source_lang")))
        self._source_lang_combo = QComboBox()
        for code, name in TARGET_LANGUAGES:
            self._source_lang_combo.addItem(name, code)
        row1.addWidget(self._source_lang_combo)
        row1.addSpacing(12)
        row1.addWidget(QLabel(t("glossary_source_term")))
        self._source_term_input = QLineEdit()
        self._source_term_input.setMinimumWidth(150)
        row1.addWidget(self._source_term_input, stretch=1)
        input_layout.addLayout(row1)

        # Row 2: Target language + target term
        row2 = QHBoxLayout()
        row2.addWidget(QLabel(t("glossary_target_lang")))
        self._target_lang_combo = QComboBox()
        for code, name in TARGET_LANGUAGES:
            self._target_lang_combo.addItem(name, code)
        # Default target to English if source is Vietnamese
        if self._target_lang_combo.count() > 1:
            self._target_lang_combo.setCurrentIndex(1)
        row2.addWidget(self._target_lang_combo)
        row2.addSpacing(12)
        row2.addWidget(QLabel(t("glossary_target_term")))
        self._target_term_input = QLineEdit()
        self._target_term_input.setMinimumWidth(150)
        row2.addWidget(self._target_term_input, stretch=1)
        input_layout.addLayout(row2)

        # Add/Update button (centered)
        add_row = QHBoxLayout()
        add_row.addStretch()
        self._add_btn = QPushButton(t("glossary_add"))
        self._add_btn.clicked.connect(self._on_add_term)
        add_row.addWidget(self._add_btn)
        add_row.addStretch()
        input_layout.addLayout(add_row)

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        # --- Search bar ---
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel(t("glossary_search")))
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("...")
        self._search_input.textChanged.connect(self._on_search)
        search_row.addWidget(self._search_input, stretch=1)
        main_layout.addLayout(search_row)

        # --- Glossary table ---
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels([
            t("glossary_col_no"),
            t("glossary_col_source"),
            t("glossary_col_source_lang"),
            t("glossary_col_target"),
            t("glossary_col_target_lang"),
        ])
        # Column sizing
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 40)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(2, 80)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(4, 80)

        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._on_table_context_menu)
        # Connect cell edit to update in-memory data
        self._table.cellChanged.connect(self._on_cell_changed)

        main_layout.addWidget(self._table, stretch=1)

        # --- Bottom buttons ---
        btn_layout = QHBoxLayout()

        import_btn = QPushButton(t("glossary_import"))
        import_btn.clicked.connect(self._on_import_csv)
        btn_layout.addWidget(import_btn)

        export_btn = QPushButton(t("glossary_export"))
        export_btn.clicked.connect(self._on_export_csv)
        btn_layout.addWidget(export_btn)

        btn_layout.addStretch()

        close_btn = QPushButton(t("glossary_close"))
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        main_layout.addLayout(btn_layout)

    # --- Table rendering ---

    def _refresh_table(self, filter_text: str = ""):
        """Re-render the table with current entries, optionally filtered."""
        self._table.blockSignals(True)  # Prevent cellChanged during refresh
        self._table.setRowCount(0)

        filter_lower = filter_text.lower()
        row_index = 0
        for source_term, source_lang, target_term, target_lang in self._entries:
            # Apply search filter
            if filter_lower and filter_lower not in source_term.lower() and filter_lower not in target_term.lower():
                continue

            self._table.insertRow(row_index)
            # # column (read-only)
            no_item = QTableWidgetItem(str(row_index + 1))
            no_item.setFlags(no_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row_index, 0, no_item)
            # Source term (editable)
            self._table.setItem(row_index, 1, QTableWidgetItem(source_term))
            # Source lang (read-only)
            sl_item = QTableWidgetItem(source_lang.upper())
            sl_item.setFlags(sl_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row_index, 2, sl_item)
            # Target term (editable)
            self._table.setItem(row_index, 3, QTableWidgetItem(target_term))
            # Target lang (read-only)
            tl_item = QTableWidgetItem(target_lang.upper())
            tl_item.setFlags(tl_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row_index, 4, tl_item)

            row_index += 1

        self._table.blockSignals(False)

    # --- Slots ---

    def _on_add_term(self):
        """Add or update a glossary term (bidirectional)."""
        source_term = self._source_term_input.text().strip()
        target_term = self._target_term_input.text().strip()
        source_lang = self._source_lang_combo.currentData()
        target_lang = self._target_lang_combo.currentData()

        if not source_term or not target_term:
            return
        if source_lang == target_lang:
            QMessageBox.warning(
                self, self._i18n.t("warning"),
                self._i18n.t("glossary_lang_same_warning"),
            )
            return

        # Add or overwrite forward entry
        self._upsert_entry(source_term, source_lang, target_term, target_lang)
        # Add or overwrite reverse entry (bidirectional)
        self._upsert_entry(target_term, target_lang, source_term, source_lang)

        # Clear inputs
        self._source_term_input.clear()
        self._target_term_input.clear()
        self._refresh_table(self._search_input.text())

    def _upsert_entry(self, source_term: str, source_lang: str, target_term: str, target_lang: str):
        """Insert or overwrite an entry matching (source_term, source_lang, target_lang)."""
        for i, (st, sl, tt, tl) in enumerate(self._entries):
            if st.lower() == source_term.lower() and sl == source_lang and tl == target_lang:
                self._entries[i] = (source_term, source_lang, target_term, target_lang)
                return
        self._entries.append((source_term, source_lang, target_term, target_lang))

    def _on_search(self, text: str):
        """Filter table by search text."""
        self._refresh_table(text)

    def _on_cell_changed(self, row: int, col: int):
        """Handle inline editing of a cell in the table."""
        # Only source_term (col=1) and target_term (col=3) are editable
        if col not in (1, 3):
            return
        item = self._table.item(row, col)
        if not item:
            return
        # Find the matching entry by row index and update it
        # Note: row in table maps to filtered view, need to find actual entry
        source_lang_item = self._table.item(row, 2)
        target_lang_item = self._table.item(row, 4)
        if not source_lang_item or not target_lang_item:
            return

        # Find the entry matching this row's original data
        old_source = self._table.item(row, 1).text() if col != 1 else None
        old_target = self._table.item(row, 3).text() if col != 3 else None
        sl = source_lang_item.text().lower()
        tl = target_lang_item.text().lower()

        for i, (st, s_lang, tt, t_lang) in enumerate(self._entries):
            if s_lang == sl and t_lang == tl:
                if col == 1:
                    self._entries[i] = (item.text(), s_lang, tt, t_lang)
                    break
                elif col == 3:
                    self._entries[i] = (st, s_lang, item.text(), t_lang)
                    break

    def _on_table_context_menu(self, pos):
        """Show context menu with delete option on right-click."""
        row = self._table.rowAt(pos.y())
        if row < 0:
            return

        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        delete_action = menu.addAction(self._i18n.t("glossary_delete"))
        action = menu.exec(self._table.viewport().mapToGlobal(pos))

        if action == delete_action:
            reply = QMessageBox.question(
                self, self._i18n.t("confirm"),
                self._i18n.t("glossary_confirm_delete"),
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._delete_row(row)

    def _delete_row(self, table_row: int):
        """Delete the entry at the given table row."""
        source_item = self._table.item(table_row, 1)
        sl_item = self._table.item(table_row, 2)
        tl_item = self._table.item(table_row, 4)
        if not source_item or not sl_item or not tl_item:
            return

        source_term = source_item.text()
        source_lang = sl_item.text().lower()
        target_lang = tl_item.text().lower()

        # Remove matching entry
        self._entries = [
            (st, sl, tt, tl)
            for st, sl, tt, tl in self._entries
            if not (st.lower() == source_term.lower() and sl == source_lang and tl == target_lang)
        ]
        self._refresh_table(self._search_input.text())

    def _on_import_csv(self):
        """Import glossary entries from a CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import CSV", "", "CSV Files (*.csv)",
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)  # Skip header row
                count = 0
                for row in reader:
                    if len(row) < 4:
                        continue
                    source_term, source_lang, target_term, target_lang = (
                        row[0].strip(), row[1].strip().lower(),
                        row[2].strip(), row[3].strip().lower(),
                    )
                    if source_term and target_term:
                        # Forward entry
                        self._upsert_entry(source_term, source_lang, target_term, target_lang)
                        # Reverse entry (bidirectional)
                        self._upsert_entry(target_term, target_lang, source_term, source_lang)
                        count += 1

            self._refresh_table(self._search_input.text())
            QMessageBox.information(
                self, "Import",
                self._i18n.t("glossary_import_success", count=count),
            )
        except Exception as e:
            QMessageBox.critical(self, self._i18n.t("error"), str(e))

    def _on_export_csv(self):
        """Export all glossary entries to a CSV file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "glossary.csv", "CSV Files (*.csv)",
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["source_term", "source_lang", "target_term", "target_lang"])
                for entry in self._entries:
                    writer.writerow(entry)

            QMessageBox.information(
                self, "Export",
                self._i18n.t("glossary_export_success",
                             count=len(self._entries),
                             filename=os.path.basename(file_path)),
            )
        except Exception as e:
            QMessageBox.critical(self, self._i18n.t("error"), str(e))

    # --- Public API ---

    def set_entries(self, entries: list[tuple[str, str, str, str]]):
        """Load entries into the dialog."""
        self._entries = list(entries)
        self._refresh_table()

    def get_entries(self) -> list[tuple[str, str, str, str]]:
        """Return all glossary entries."""
        return list(self._entries)
