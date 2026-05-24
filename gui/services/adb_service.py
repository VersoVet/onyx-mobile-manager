"""Service ADB local pour la gestion des appareils Android."""

import subprocess
from dataclasses import dataclass


@dataclass
class ADBResult:
    """Resultat d'une commande ADB."""

    success: bool
    output: str
    error: str


class ADBService:
    """Wrapper autour de la CLI adb pour gerer les appareils Android.

    Utilise subprocess pour appeler adb installe localement.
    """

    def __init__(self, adb_path: str = "adb") -> None:
        """Initialise le service ADB.

        Args:
            adb_path: Chemin vers l'executable adb.
        """
        self.adb_path = adb_path

    def _run(self, args: list[str], timeout: int = 30) -> ADBResult:
        """Execute une commande ADB.

        Args:
            args: Arguments de la commande adb.
            timeout: Timeout en secondes.

        Returns:
            Resultat de la commande.
        """
        try:
            result = subprocess.run(
                [self.adb_path, *args],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return ADBResult(
                success=result.returncode == 0,
                output=result.stdout.strip(),
                error=result.stderr.strip(),
            )
        except subprocess.TimeoutExpired:
            return ADBResult(success=False, output="", error="Timeout ADB")
        except FileNotFoundError:
            return ADBResult(
                success=False,
                output="",
                error="adb non trouve. Verifier l'installation.",
            )

    def list_devices(self) -> list[dict[str, str]]:
        """Liste les appareils ADB connectes.

        Returns:
            Liste de dicts avec serial et status pour chaque appareil.
        """
        result = self._run(["devices", "-l"])
        if not result.success:
            return []
        devices = []
        for line in result.output.splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 2:
                info: dict[str, str] = {"serial": parts[0], "status": parts[1]}
                for part in parts[2:]:
                    if ":" in part:
                        key, val = part.split(":", 1)
                        info[key] = val
                devices.append(info)
        return devices

    def connect(self, ip: str, port: int = 5555) -> ADBResult:
        """Connecte un appareil via WiFi ADB.

        Args:
            ip: Adresse IP de l'appareil.
            port: Port ADB (defaut 5555).

        Returns:
            Resultat de la connexion.
        """
        return self._run(["connect", f"{ip}:{port}"])

    def disconnect(self, ip: str, port: int = 5555) -> ADBResult:
        """Deconnecte un appareil WiFi ADB.

        Args:
            ip: Adresse IP de l'appareil.
            port: Port ADB (defaut 5555).

        Returns:
            Resultat de la deconnexion.
        """
        return self._run(["disconnect", f"{ip}:{port}"])

    def install_apk(self, serial: str, apk_path: str) -> ADBResult:
        """Installe un APK sur un appareil.

        Args:
            serial: Serial ou IP:port de l'appareil.
            apk_path: Chemin local du fichier APK.

        Returns:
            Resultat de l'installation.
        """
        return self._run(["-s", serial, "install", "-r", apk_path], timeout=120)

    def uninstall_package(self, serial: str, package: str) -> ADBResult:
        """Desinstalle un package d'un appareil.

        Args:
            serial: Serial ou IP:port de l'appareil.
            package: Nom du package (ex: com.onyx.dashboard).

        Returns:
            Resultat de la desinstallation.
        """
        return self._run(["-s", serial, "uninstall", package])

    def push_file(self, serial: str, local_path: str, remote_path: str) -> ADBResult:
        """Pousse un fichier vers l'appareil.

        Args:
            serial: Serial ou IP:port de l'appareil.
            local_path: Chemin local du fichier.
            remote_path: Chemin destination sur l'appareil.

        Returns:
            Resultat du push.
        """
        return self._run(["-s", serial, "push", local_path, remote_path])

    def pull_file(self, serial: str, remote_path: str, local_path: str) -> ADBResult:
        """Recupere un fichier depuis l'appareil.

        Args:
            serial: Serial ou IP:port de l'appareil.
            remote_path: Chemin sur l'appareil.
            local_path: Chemin local destination.

        Returns:
            Resultat du pull.
        """
        return self._run(["-s", serial, "pull", remote_path, local_path])

    def shell(self, serial: str, command: str) -> ADBResult:
        """Execute une commande shell sur l'appareil.

        Args:
            serial: Serial ou IP:port de l'appareil.
            command: Commande shell a executer.

        Returns:
            Resultat de la commande.
        """
        return self._run(["-s", serial, "shell", command])

    def reboot(self, serial: str) -> ADBResult:
        """Redemarre l'appareil.

        Args:
            serial: Serial ou IP:port de l'appareil.

        Returns:
            Resultat du reboot.
        """
        return self._run(["-s", serial, "reboot"])

    def get_device_model(self, serial: str) -> str:
        """Recupere le modele de l'appareil.

        Args:
            serial: Serial ou IP:port de l'appareil.

        Returns:
            Nom du modele ou chaine vide si erreur.
        """
        result = self.shell(serial, "getprop ro.product.model")
        return result.output if result.success else ""

    def get_android_version(self, serial: str) -> str:
        """Recupere la version Android de l'appareil.

        Args:
            serial: Serial ou IP:port de l'appareil.

        Returns:
            Version Android ou chaine vide si erreur.
        """
        result = self.shell(serial, "getprop ro.build.version.release")
        return result.output if result.success else ""

    def list_installed_packages(self, serial: str) -> list[str]:
        """Liste les packages installes sur l'appareil.

        Args:
            serial: Serial ou IP:port de l'appareil.

        Returns:
            Liste des noms de packages.
        """
        result = self.shell(serial, "pm list packages")
        if not result.success:
            return []
        return [line.replace("package:", "") for line in result.output.splitlines()]
