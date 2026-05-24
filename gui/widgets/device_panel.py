"""Panel de gestion des appareils mobiles."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from gui.services.adb_service import ADBService
from gui.services.api_client import APIClient

COLUMNS = ["Nom", "Type", "Modele", "Serial", "IP", "Port", "Statut"]


class DevicePanel(QWidget):
    """Panel pour lister, ajouter et gerer les appareils."""

    def __init__(self, api: APIClient, adb: ADBService) -> None:
        """Initialise le panel appareils.

        Args:
            api: Client API backend.
            adb: Service ADB local.
        """
        super().__init__()
        self.api = api
        self.adb = adb
        self._device_ids: list[str] = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self) -> None:
        """Configure l'interface du panel."""
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        btn_add = QPushButton("Ajouter")
        btn_add.clicked.connect(self._add_device)
        btn_scan = QPushButton("Scanner ADB")
        btn_scan.clicked.connect(self._scan_adb)
        btn_refresh = QPushButton("Rafraichir")
        btn_refresh.clicked.connect(self.refresh)
        btn_delete = QPushButton("Supprimer")
        btn_delete.clicked.connect(self._delete_device)
        toolbar.addWidget(btn_add)
        toolbar.addWidget(btn_scan)
        toolbar.addWidget(btn_refresh)
        toolbar.addWidget(btn_delete)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.lbl_status = QLabel("")
        layout.addWidget(self.lbl_status)

    def refresh(self) -> None:
        """Rafraichit la liste des appareils depuis le backend."""
        try:
            devices = self.api.list_devices()
            self._device_ids = [d["id"] for d in devices]
            self.table.setRowCount(len(devices))
            for row, dev in enumerate(devices):
                for col, key in enumerate(
                    [
                        "name",
                        "device_type",
                        "model",
                        "serial",
                        "ip_address",
                        "adb_port",
                        "status",
                    ]
                ):
                    item = QTableWidgetItem(str(dev.get(key, "")))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row, col, item)
            self.lbl_status.setText(f"{len(devices)} appareil(s)")
        except Exception as e:
            self.lbl_status.setText(f"Erreur: {e}")

    def _add_device(self) -> None:
        """Ouvre le dialogue d'ajout d'appareil."""
        dialog = AddDeviceDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                self.api.create_device(data)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "Erreur", str(e))

    def _delete_device(self) -> None:
        """Supprime l'appareil selectionne."""
        row = self.table.currentRow()
        if row < 0 or row >= len(self._device_ids):
            return
        device_id = self._device_ids[row]
        name = self.table.item(row, 0).text() if self.table.item(row, 0) else "?"
        reply = QMessageBox.question(
            self,
            "Confirmer",
            f"Supprimer {name} ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api.delete_device(device_id)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "Erreur", str(e))

    def _scan_adb(self) -> None:
        """Scanne les appareils ADB connectes localement."""
        devices = self.adb.list_devices()
        if not devices:
            self.lbl_status.setText("Aucun appareil ADB detecte")
            return
        msg = "\n".join(f"{d['serial']} ({d['status']})" for d in devices)
        QMessageBox.information(self, "Appareils ADB", f"Detectes:\n{msg}")

    def get_selected_device_id(self) -> str | None:
        """Retourne l'ID de l'appareil selectionne.

        Returns:
            UUID de l'appareil ou None.
        """
        row = self.table.currentRow()
        if row < 0 or row >= len(self._device_ids):
            return None
        return self._device_ids[row]

    def get_selected_device(self) -> dict[str, str] | None:
        """Retourne les infos de l'appareil selectionne.

        Returns:
            Dict avec serial et ip_address, ou None.
        """
        row = self.table.currentRow()
        if row < 0:
            return None
        serial = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
        ip = self.table.item(row, 4).text() if self.table.item(row, 4) else ""
        port = self.table.item(row, 5).text() if self.table.item(row, 5) else "5555"
        return {"serial": serial, "ip_address": ip, "adb_port": port}


class AddDeviceDialog(QDialog):
    """Dialogue pour ajouter un nouvel appareil."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialise le dialogue d'ajout.

        Args:
            parent: Widget parent.
        """
        super().__init__(parent)
        self.setWindowTitle("Ajouter un appareil")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["phone", "tablet"])
        self.model_input = QLineEdit()
        self.serial_input = QLineEdit()
        self.ip_input = QLineEdit()
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(5555)
        self.notes_input = QLineEdit()

        layout.addRow("Nom:", self.name_input)
        layout.addRow("Type:", self.type_combo)
        layout.addRow("Modele:", self.model_input)
        layout.addRow("Serial ADB:", self.serial_input)
        layout.addRow("Adresse IP:", self.ip_input)
        layout.addRow("Port ADB:", self.port_input)
        layout.addRow("Notes:", self.notes_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self) -> dict[str, str | int]:
        """Retourne les donnees saisies.

        Returns:
            Dict avec les champs de l'appareil.
        """
        return {
            "name": self.name_input.text(),
            "device_type": self.type_combo.currentText(),
            "model": self.model_input.text(),
            "serial": self.serial_input.text(),
            "ip_address": self.ip_input.text(),
            "adb_port": self.port_input.value(),
            "notes": self.notes_input.text(),
        }
