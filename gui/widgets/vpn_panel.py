"""Panel de configuration VPN pour les appareils."""

from PyQt6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gui.services.adb_service import ADBService
from gui.services.api_client import APIClient
from gui.services.vpn_service import VPNService


class VPNPanel(QWidget):
    """Panel pour configurer et deployer des profils VPN WireGuard."""

    def __init__(self, api: APIClient, adb: ADBService, vpn: VPNService) -> None:
        """Initialise le panel VPN.

        Args:
            api: Client API backend.
            adb: Service ADB local.
            vpn: Service VPN.
        """
        super().__init__()
        self.api = api
        self.adb = adb
        self.vpn = vpn
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configure l'interface du panel VPN."""
        layout = QVBoxLayout(self)

        config_group = QGroupBox("Configuration WireGuard")
        form = QFormLayout(config_group)
        self.private_key = QLineEdit()
        self.private_key.setPlaceholderText("Cle privee du client")
        self.private_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.server_pubkey = QLineEdit()
        self.server_pubkey.setPlaceholderText("Cle publique du serveur")
        self.server_endpoint = QLineEdit()
        self.server_endpoint.setPlaceholderText("ex: vpn.onyx.local:51820")
        self.client_address = QLineEdit()
        self.client_address.setPlaceholderText("ex: 10.10.0.2/32")
        self.allowed_ips = QLineEdit("10.0.0.0/24")
        self.dns_server = QLineEdit("10.0.0.1")

        form.addRow("Cle privee client:", self.private_key)
        form.addRow("Cle publique serveur:", self.server_pubkey)
        form.addRow("Endpoint serveur:", self.server_endpoint)
        form.addRow("Adresse client:", self.client_address)
        form.addRow("IPs autorisees:", self.allowed_ips)
        form.addRow("DNS:", self.dns_server)
        layout.addWidget(config_group)

        actions = QHBoxLayout()
        btn_generate = QPushButton("Generer config")
        btn_generate.clicked.connect(self._generate_config)
        btn_push = QPushButton("Pousser sur appareil")
        btn_push.clicked.connect(self._push_config)
        btn_check = QPushButton("Verifier VPN")
        btn_check.clicked.connect(self._check_vpn)
        actions.addWidget(btn_generate)
        actions.addWidget(btn_push)
        actions.addWidget(btn_check)
        layout.addLayout(actions)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("Apercu de la configuration generee...")
        layout.addWidget(self.preview)

        self.lbl_status = QLabel("")
        layout.addWidget(self.lbl_status)

    def _generate_config(self) -> None:
        """Genere un fichier de configuration WireGuard."""
        config = self.vpn.generate_wireguard_config(
            device_name="device",
            private_key=self.private_key.text(),
            server_public_key=self.server_pubkey.text(),
            server_endpoint=self.server_endpoint.text(),
            allowed_ips=self.allowed_ips.text(),
            dns=self.dns_server.text(),
            address=self.client_address.text(),
        )
        self.preview.setPlainText(config)
        self.lbl_status.setText("Configuration generee")

    def _push_config(self) -> None:
        """Pousse la config VPN sur l'appareil selectionne via ADB."""
        config_text = self.preview.toPlainText()
        if not config_text:
            QMessageBox.warning(self, "Erreur", "Generez d'abord la configuration")
            return

        main_win = self.window()
        device_panel = getattr(main_win, "device_panel", None)
        if device_panel is None:
            self.lbl_status.setText("Erreur: panel appareils introuvable")
            return

        device = device_panel.get_selected_device()
        if device is None:
            QMessageBox.warning(
                self, "Erreur", "Selectionnez un appareil dans l'onglet Appareils"
            )
            return

        serial = device.get("serial") or f"{device['ip_address']}:{device['adb_port']}"
        result = self.vpn.push_vpn_config(serial, config_text)
        if result.success:
            self.lbl_status.setText(f"Config VPN poussee sur {serial}")
            self._log_action(
                device_panel, "vpn_configure", f"WireGuard config pushed to {serial}"
            )
        else:
            self.lbl_status.setText(f"Echec: {result.error}")

    def _check_vpn(self) -> None:
        """Verifie le statut VPN sur l'appareil selectionne."""
        main_win = self.window()
        device_panel = getattr(main_win, "device_panel", None)
        if device_panel is None:
            return

        device = device_panel.get_selected_device()
        if device is None:
            QMessageBox.warning(self, "Info", "Selectionnez un appareil")
            return

        serial = device.get("serial") or f"{device['ip_address']}:{device['adb_port']}"
        status = self.vpn.check_vpn_status(serial)
        reachable = self.vpn.check_onyx_reachability(serial)

        msg = f"VPN: {'Connecte' if status['connected'] == 'true' else 'Deconnecte'}\n"
        msg += f"Reseau Onyx: {'Accessible' if reachable else 'Inaccessible'}"
        QMessageBox.information(self, "Statut VPN", msg)

    def _log_action(self, device_panel: object, action: str, details: str) -> None:
        """Logge une action dans l'historique via le backend.

        Args:
            device_panel: Panel des appareils pour obtenir l'ID.
            action: Type d'action.
            details: Details de l'action.
        """
        device_id = getattr(device_panel, "get_selected_device_id", lambda: None)()
        if device_id:
            try:
                self.api.log_action(
                    {
                        "device_id": device_id,
                        "action": action,
                        "details": details,
                        "operator": "gui_user",
                    }
                )
            except Exception:
                pass
