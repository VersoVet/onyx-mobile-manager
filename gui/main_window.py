"""Fenetre principale de l'application Onyx Mobile Manager."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QLabel,
    QMainWindow,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from gui.services.adb_service import ADBService
from gui.services.api_client import APIClient
from gui.services.vpn_service import VPNService
from gui.widgets.apk_panel import APKPanel
from gui.widgets.device_panel import DevicePanel
from gui.widgets.history_panel import HistoryPanel
from gui.widgets.vpn_panel import VPNPanel

DEFAULT_BACKEND_URL = "http://172.16.0.3:8095"


class MainWindow(QMainWindow):
    """Fenetre principale avec onglets pour gerer les appareils mobiles."""

    def __init__(self) -> None:
        """Initialise la fenetre, les services et les onglets."""
        super().__init__()
        self.setWindowTitle("Onyx Mobile Manager")
        self.setMinimumSize(900, 600)

        self.api = APIClient(DEFAULT_BACKEND_URL)
        self.adb = ADBService()
        self.vpn = VPNService(self.adb)

        self._setup_ui()
        self._check_backend()

    def _setup_ui(self) -> None:
        """Configure l'interface avec les onglets."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        header = QLabel("Onyx Mobile Manager")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 8px;")
        layout.addWidget(header)

        self.tabs = QTabWidget()
        self.device_panel = DevicePanel(self.api, self.adb)
        self.vpn_panel = VPNPanel(self.api, self.adb, self.vpn)
        self.apk_panel = APKPanel(self.api, self.adb)
        self.history_panel = HistoryPanel(self.api)

        self.tabs.addTab(self.device_panel, "Appareils")
        self.tabs.addTab(self.vpn_panel, "VPN")
        self.tabs.addTab(self.apk_panel, "APKs")
        self.tabs.addTab(self.history_panel, "Historique")
        layout.addWidget(self.tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._status_label = QLabel("Deconnecte")
        self.status_bar.addPermanentWidget(self._status_label)

    def _check_backend(self) -> None:
        """Verifie la connexion au backend Soma."""
        try:
            result = self.api.health()
            version = result.get("version", "?")
            self._status_label.setText(f"Connecte - Backend v{version}")
            self._status_label.setStyleSheet("color: green;")
        except Exception:
            self._status_label.setText("Backend inaccessible")
            self._status_label.setStyleSheet("color: red;")

    def closeEvent(self, event: object) -> None:
        """Ferme proprement les connexions a la fermeture.

        Args:
            event: Evenement de fermeture.
        """
        self.api.close()
        super().closeEvent(event)  # type: ignore[arg-type]
