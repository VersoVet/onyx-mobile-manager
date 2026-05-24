"""Client HTTP pour communiquer avec le backend Soma."""

from typing import Any

import httpx


class APIClient:
    """Client HTTP synchrone pour le backend onyx-mobile-manager.

    Utilise httpx en mode synchrone car PyQt6 tourne dans le thread principal.
    Les appels reseau sont courts et le backend est sur le LAN.
    """

    def __init__(self, base_url: str = "http://172.16.0.3:8095") -> None:
        """Initialise le client API.

        Args:
            base_url: URL de base du backend Soma.
        """
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=30.0)

    def close(self) -> None:
        """Ferme le client HTTP."""
        self._client.close()

    # --- Health ---

    def health(self) -> dict[str, Any]:
        """Verifie la sante du backend.

        Returns:
            Reponse health du backend.
        """
        r = self._client.get("/health")
        r.raise_for_status()
        return r.json()

    # --- Devices ---

    def list_devices(self) -> list[dict[str, Any]]:
        """Liste tous les appareils enregistres.

        Returns:
            Liste des appareils.
        """
        r = self._client.get("/api/devices")
        r.raise_for_status()
        return r.json()

    def create_device(self, data: dict[str, Any]) -> dict[str, Any]:
        """Enregistre un nouvel appareil.

        Args:
            data: Donnees de l'appareil (name, device_type, model, serial, ip_address, adb_port).

        Returns:
            Appareil cree avec son ID.
        """
        r = self._client.post("/api/devices", json=data)
        r.raise_for_status()
        return r.json()

    def update_device(self, device_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Modifie un appareil existant.

        Args:
            device_id: ID de l'appareil.
            data: Champs a modifier.

        Returns:
            Appareil mis a jour.
        """
        r = self._client.put(f"/api/devices/{device_id}", json=data)
        r.raise_for_status()
        return r.json()

    def delete_device(self, device_id: str) -> dict[str, Any]:
        """Supprime un appareil.

        Args:
            device_id: ID de l'appareil.

        Returns:
            Confirmation de suppression.
        """
        r = self._client.delete(f"/api/devices/{device_id}")
        r.raise_for_status()
        return r.json()

    def update_device_status(self, device_id: str, status: str) -> dict[str, Any]:
        """Met a jour le statut d'un appareil.

        Args:
            device_id: ID de l'appareil.
            status: Nouveau statut (online, offline, maintenance).

        Returns:
            Appareil mis a jour.
        """
        r = self._client.patch(
            f"/api/devices/{device_id}/status", json={"status": status}
        )
        r.raise_for_status()
        return r.json()

    # --- History ---

    def get_history(
        self,
        device_id: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Recupere l'historique des actions.

        Args:
            device_id: Filtre par appareil.
            action: Filtre par type d'action.
            limit: Nombre max d'entrees.

        Returns:
            Liste des entrees d'historique.
        """
        params: dict[str, Any] = {"limit": limit}
        if device_id:
            params["device_id"] = device_id
        if action:
            params["action"] = action
        r = self._client.get("/api/history", params=params)
        r.raise_for_status()
        return r.json()

    def log_action(self, data: dict[str, Any]) -> dict[str, Any]:
        """Logge une action dans l'historique.

        Args:
            data: Donnees de l'action (device_id, action, details, operator, success).

        Returns:
            Entree d'historique creee.
        """
        r = self._client.post("/api/history", json=data)
        r.raise_for_status()
        return r.json()

    def export_history(self, fmt: str = "json") -> bytes:
        """Exporte l'historique complet.

        Args:
            fmt: Format d'export (json ou csv).

        Returns:
            Contenu du fichier exporte.
        """
        r = self._client.get("/api/history/export", params={"format": fmt})
        r.raise_for_status()
        return r.content

    # --- APK ---

    def list_apks(self) -> list[dict[str, Any]]:
        """Liste les APKs disponibles.

        Returns:
            Liste des informations APK.
        """
        r = self._client.get("/api/apk")
        r.raise_for_status()
        return r.json()

    def upload_apk(
        self, filepath: str, version: str, description: str = ""
    ) -> dict[str, Any]:
        """Upload un APK vers le backend.

        Args:
            filepath: Chemin local du fichier APK.
            version: Version de l'APK.
            description: Description optionnelle.

        Returns:
            Informations de l'APK uploade.
        """
        with open(filepath, "rb") as f:
            r = self._client.post(
                "/api/apk/upload",
                files={
                    "file": (
                        filepath.split("/")[-1],
                        f,
                        "application/vnd.android.package-archive",
                    )
                },
                data={"version": version, "description": description},
            )
        r.raise_for_status()
        return r.json()

    def download_apk(self, name: str) -> bytes:
        """Telecharge un APK depuis le backend.

        Args:
            name: Nom de l'APK.

        Returns:
            Contenu binaire du fichier APK.
        """
        r = self._client.get(f"/api/apk/{name}/download")
        r.raise_for_status()
        return r.content

    def delete_apk(self, name: str) -> dict[str, Any]:
        """Supprime un APK du backend.

        Args:
            name: Nom de l'APK.

        Returns:
            Confirmation de suppression.
        """
        r = self._client.delete(f"/api/apk/{name}")
        r.raise_for_status()
        return r.json()
