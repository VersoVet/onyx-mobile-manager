"""Panel de gestion des APKs Onyx."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from gui.services.adb_service import ADBService
from gui.services.api_client import APIClient

APK_COLUMNS = ["Nom", "Version", "Taille", "Description", "Date upload"]


class APKPanel(QWidget):
    """Panel pour gerer les APKs: upload, install sur appareil, suppression."""

    def __init__(self, api: APIClient, adb: ADBService) -> None:
        """Initialise le panel APK.

        Args:
            api: Client API backend.
            adb: Service ADB local.
        """
        super().__init__()
        self.api = api
        self.adb = adb
        self._apk_names: list[str] = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self) -> None:
        """Configure l'interface du panel."""
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        btn_upload = QPushButton("Upload APK")
        btn_upload.clicked.connect(self._upload_apk)
        btn_install = QPushButton("Installer sur appareil")
        btn_install.clicked.connect(self._install_on_device)
        btn_delete = QPushButton("Supprimer")
        btn_delete.clicked.connect(self._delete_apk)
        btn_refresh = QPushButton("Rafraichir")
        btn_refresh.clicked.connect(self.refresh)
        toolbar.addWidget(btn_upload)
        toolbar.addWidget(btn_install)
        toolbar.addWidget(btn_delete)
        toolbar.addWidget(btn_refresh)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, len(APK_COLUMNS))
        self.table.setHorizontalHeaderLabels(APK_COLUMNS)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.lbl_status = QLabel("")
        layout.addWidget(self.lbl_status)

    def refresh(self) -> None:
        """Rafraichit la liste des APKs depuis le backend."""
        try:
            apks = self.api.list_apks()
            self._apk_names = [a["name"] for a in apks]
            self.table.setRowCount(len(apks))
            for row, apk in enumerate(apks):
                size_mb = f"{apk.get('size_bytes', 0) / 1024 / 1024:.1f} Mo"
                values = [
                    apk.get("name", ""),
                    apk.get("version", ""),
                    size_mb,
                    apk.get("description", ""),
                    apk.get("uploaded_at", "")[:19],
                ]
                for col, val in enumerate(values):
                    item = QTableWidgetItem(str(val))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row, col, item)
            self.lbl_status.setText(f"{len(apks)} APK(s) disponible(s)")
        except Exception as e:
            self.lbl_status.setText(f"Erreur: {e}")

    def _upload_apk(self) -> None:
        """Ouvre un dialogue pour uploader un APK."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Selectionner un APK", "", "APK Files (*.apk)"
        )
        if not filepath:
            return
        version, ok = QInputDialog.getText(
            self, "Version", "Version de l'APK:", text="1.0.0"
        )
        if not ok:
            return
        desc, _ = QInputDialog.getText(self, "Description", "Description:")
        try:
            self.api.upload_apk(filepath, version, desc)
            self.refresh()
            self.lbl_status.setText("APK uploade avec succes")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def _install_on_device(self) -> None:
        """Installe l'APK selectionne sur l'appareil selectionne."""
        row = self.table.currentRow()
        if row < 0 or row >= len(self._apk_names):
            QMessageBox.warning(self, "Info", "Selectionnez un APK")
            return

        main_win = self.window()
        device_panel = getattr(main_win, "device_panel", None)
        if device_panel is None:
            return

        device = device_panel.get_selected_device()
        if device is None:
            QMessageBox.warning(
                self, "Info", "Selectionnez un appareil dans l'onglet Appareils"
            )
            return

        apk_name = self._apk_names[row]
        serial = device.get("serial") or f"{device['ip_address']}:{device['adb_port']}"

        try:
            apk_content = self.api.download_apk(apk_name)
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".apk", delete=False) as tmp:
                tmp.write(apk_content)
                tmp_path = tmp.name

            result = self.adb.install_apk(serial, tmp_path)
            if result.success:
                self.lbl_status.setText(f"{apk_name} installe sur {serial}")
                device_id = device_panel.get_selected_device_id()
                if device_id:
                    self.api.log_action(
                        {
                            "device_id": device_id,
                            "action": "apk_install",
                            "details": f"Installed {apk_name} on {serial}",
                            "operator": "gui_user",
                        }
                    )
            else:
                self.lbl_status.setText(f"Echec: {result.error}")

            import os

            os.unlink(tmp_path)
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def _delete_apk(self) -> None:
        """Supprime l'APK selectionne du backend."""
        row = self.table.currentRow()
        if row < 0 or row >= len(self._apk_names):
            return
        name = self._apk_names[row]
        reply = QMessageBox.question(
            self,
            "Confirmer",
            f"Supprimer l'APK {name} ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api.delete_apk(name)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "Erreur", str(e))
