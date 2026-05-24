"""Panel d'historique et audit trail."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from gui.services.api_client import APIClient

HISTORY_COLUMNS = ["Date", "Appareil", "Action", "Details", "Operateur", "Succes"]

ACTION_TYPES = [
    "",
    "apk_install",
    "apk_uninstall",
    "apk_update",
    "vpn_configure",
    "vpn_remove",
    "adb_connect",
    "adb_disconnect",
    "config_push",
    "shell_command",
    "reboot",
    "device_register",
    "device_remove",
    "other",
]


class HistoryPanel(QWidget):
    """Panel pour consulter et exporter l'historique des modifications."""

    def __init__(self, api: APIClient) -> None:
        """Initialise le panel historique.

        Args:
            api: Client API backend.
        """
        super().__init__()
        self.api = api
        self._setup_ui()
        self.refresh()

    def _setup_ui(self) -> None:
        """Configure l'interface du panel."""
        layout = QVBoxLayout(self)

        filters = QHBoxLayout()
        filters.addWidget(QLabel("Appareil ID:"))
        self.filter_device = QLineEdit()
        self.filter_device.setPlaceholderText("Tous")
        filters.addWidget(self.filter_device)

        filters.addWidget(QLabel("Action:"))
        self.filter_action = QComboBox()
        self.filter_action.addItems(ACTION_TYPES)
        filters.addWidget(self.filter_action)

        btn_filter = QPushButton("Filtrer")
        btn_filter.clicked.connect(self.refresh)
        btn_export = QPushButton("Exporter CSV")
        btn_export.clicked.connect(self._export_csv)
        filters.addWidget(btn_filter)
        filters.addWidget(btn_export)
        layout.addLayout(filters)

        self.table = QTableWidget(0, len(HISTORY_COLUMNS))
        self.table.setHorizontalHeaderLabels(HISTORY_COLUMNS)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.lbl_status = QLabel("")
        layout.addWidget(self.lbl_status)

    def refresh(self) -> None:
        """Rafraichit l'historique avec les filtres appliques."""
        device_id = self.filter_device.text().strip() or None
        action = self.filter_action.currentText() or None
        try:
            entries = self.api.get_history(device_id=device_id, action=action)
            self.table.setRowCount(len(entries))
            for row, entry in enumerate(entries):
                values = [
                    entry.get("timestamp", "")[:19],
                    entry.get("device_name", "") or entry.get("device_id", ""),
                    entry.get("action", ""),
                    entry.get("details", ""),
                    entry.get("operator", ""),
                    "OK" if entry.get("success") else "ECHEC",
                ]
                for col, val in enumerate(values):
                    item = QTableWidgetItem(str(val))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    if col == 5 and val == "ECHEC":
                        item.setForeground(Qt.GlobalColor.red)
                    self.table.setItem(row, col, item)
            self.lbl_status.setText(f"{len(entries)} entree(s)")
        except Exception as e:
            self.lbl_status.setText(f"Erreur: {e}")

    def _export_csv(self) -> None:
        """Exporte l'historique en CSV via le backend."""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Exporter l'historique", "history_export.csv", "CSV Files (*.csv)"
        )
        if not filepath:
            return
        try:
            content = self.api.export_history(fmt="csv")
            with open(filepath, "wb") as f:
                f.write(content)
            self.lbl_status.setText(f"Exporte vers {filepath}")
        except Exception as e:
            self.lbl_status.setText(f"Erreur export: {e}")
