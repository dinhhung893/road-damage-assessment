"""Damage summary table widget — shows per-damage records with PCI summary."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QHeaderView,
)

from src.ui.strings import (
    get_string,
    get_damage_type_name,
    get_severity_name,
    get_rating_name,
)

# Severity row colors
SEVERITY_COLORS = {
    "Low": QColor(46, 204, 113, 40),      # light green
    "Medium": QColor(241, 196, 15, 40),    # light yellow
    "High": QColor(231, 76, 60, 40),       # light red
}

# Column keys (order matters)
COLUMNS = [
    "table_code",
    "table_type",
    "table_severity",
    "table_density",
    "table_deduct",
    "table_confidence",
]


class DamageTable(QWidget):
    """Damage summary table with PCI result footer.

    Shows one row per damage record with localized column headers,
    severity color-coding, and a summary footer with PCI score.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(4)

        # Table title
        self._title_label = QLabel(get_string("pci_title"))
        self._title_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        self._layout.addWidget(self._title_label)

        # Table
        self._table = QTableWidget(0, len(COLUMNS), self)
        self._table.setHorizontalHeaderLabels([get_string(c) for c in COLUMNS])
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)

        # Stretch last column
        header = self._table.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(len(COLUMNS) - 1):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        self._layout.addWidget(self._table)

        # Summary label (PCI score + rating + CDV + maintenance)
        self._summary_label = QLabel(get_string("table_no_data"))
        self._summary_label.setWordWrap(True)
        self._summary_label.setStyleSheet("font-size: 12px; padding: 4px;")
        self._layout.addWidget(self._summary_label)

        self.setMinimumWidth(250)

    def update_from_pci_result(self, pci_result) -> None:
        """Populate table from a PCIResult object.

        Args:
            pci_result: PCIResult dataclass with damages, pci_value, rating, cdv, etc.
        """
        self._table.setRowCount(0)

        if pci_result is None or not pci_result.damages:
            self._summary_label.setText(get_string("table_no_data"))
            return

        # Populate rows
        for i, dmg in enumerate(pci_result.damages):
            row = self._table.rowCount()
            self._table.insertRow(row)

            code = getattr(dmg, "code", "UNKNOWN")
            severity = getattr(dmg, "severity", "Low")
            density = getattr(dmg, "density_pct", 0.0)
            deduct = getattr(dmg, "deduct_value", 0.0)
            confidence = getattr(dmg, "confidence", 0.0)

            items = [
                code,
                get_damage_type_name(code),
                get_severity_name(severity),
                f"{density:.2f}",
                f"{deduct:.1f}",
                f"{confidence:.0%}",
            ]

            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Color-code by severity
                bg_color = SEVERITY_COLORS.get(severity, QColor(0, 0, 0, 0))
                item.setBackground(bg_color)

                self._table.setItem(row, col, item)

        # Summary
        pci_val = pci_result.pci_value
        rating = pci_result.rating
        cdv = pci_result.cdv
        rating_name = get_rating_name(rating)

        maintenance_action = ""
        maintenance_detail = ""
        if hasattr(pci_result, "maintenance_action") and pci_result.maintenance_action:
            maintenance_action = pci_result.maintenance_action
        if hasattr(pci_result, "maintenance_detail") and pci_result.maintenance_detail:
            maintenance_detail = pci_result.maintenance_detail

        summary = (
            f"PCI = {pci_val:.1f} ({rating_name})  |  "
            f"CDV = {cdv:.1f}  |  "
            f"{get_string('pci_maintenance')}: {maintenance_action}"
        )
        if maintenance_detail:
            summary += f" — {maintenance_detail}"

        self._summary_label.setText(summary)

    def reset(self) -> None:
        """Clear the table and summary."""
        self._table.setRowCount(0)
        self._summary_label.setText(get_string("table_no_data"))

    def update_strings(self) -> None:
        """Update all displayed strings (e.g. after language change)."""
        self._title_label.setText(get_string("pci_title"))
        self._table.setHorizontalHeaderLabels([get_string(c) for c in COLUMNS])
