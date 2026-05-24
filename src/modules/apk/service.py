"""Service de gestion des fichiers APK et versioning."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from src.config import APK_DIR
from src.models import APKInfo


async def init_storage() -> None:
    """Initialise le repertoire de stockage des APKs.

    Cree le dossier APK_DIR s'il n'existe pas encore.
    """
    APK_DIR.mkdir(parents=True, exist_ok=True)


def _meta_path(apk_path: Path) -> Path:
    """Retourne le chemin du fichier metadata JSON sidecar."""
    return apk_path.with_suffix(".meta.json")


def _read_meta(meta_file: Path) -> dict[str, str] | None:
    """Lit un fichier metadata JSON sidecar."""
    try:
        with open(meta_file) as f:
            result: dict[str, str] = json.load(f)
            return result
    except (OSError, json.JSONDecodeError):
        return None


def _build_apk_info(apk_file: Path, meta: dict[str, str]) -> APKInfo:
    """Construit un APKInfo depuis un fichier APK et ses metadonnees."""
    return APKInfo(
        name=apk_file.stem,
        filename=apk_file.name,
        version=str(meta.get("version", "unknown")),
        size_bytes=apk_file.stat().st_size,
        description=str(meta.get("description", "")),
        uploaded_at=str(meta.get("uploaded_at", "")),
        checksum_sha256=str(meta.get("checksum_sha256", "")),
    )


async def list_apks() -> list[APKInfo]:
    """Liste tous les APKs disponibles avec leurs metadonnees.

    Scanne APK_DIR pour les fichiers .apk et lit les .meta.json associes.

    Returns:
        Liste des APKInfo tries par nom.
    """
    await init_storage()
    results: list[APKInfo] = []
    for apk_file in sorted(APK_DIR.glob("*.apk")):
        meta = _read_meta(_meta_path(apk_file))
        if meta is not None:
            results.append(_build_apk_info(apk_file, meta))
    return results


async def get_apk_info(name: str) -> APKInfo | None:
    """Recupere les informations d'un APK par son nom.

    Args:
        name: Nom de l'APK (sans extension .apk).

    Returns:
        APKInfo si trouve, None sinon.
    """
    apk_file = APK_DIR / f"{name}.apk"
    if not apk_file.exists():
        return None
    meta = _read_meta(_meta_path(apk_file))
    if meta is None:
        return None
    return _build_apk_info(apk_file, meta)


async def save_apk(
    filename: str,
    content: bytes,
    version: str,
    description: str,
) -> APKInfo:
    """Sauvegarde un fichier APK avec ses metadonnees.

    Args:
        filename: Nom du fichier APK (ex: app.apk).
        content: Contenu binaire du fichier APK.
        version: Version de l'APK (ex: 1.2.3).
        description: Description de l'APK.

    Returns:
        APKInfo de l'APK sauvegarde.
    """
    await init_storage()
    if not filename.endswith(".apk"):
        filename = f"{filename}.apk"
    apk_path = APK_DIR / filename
    checksum = hashlib.sha256(content).hexdigest()
    apk_path.write_bytes(content)
    meta = {
        "version": version,
        "description": description,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "checksum_sha256": checksum,
    }
    with open(_meta_path(apk_path), "w") as f:
        json.dump(meta, f, indent=2)
    return _build_apk_info(apk_path, meta)


async def delete_apk(name: str) -> bool:
    """Supprime un APK et son fichier metadata.

    Args:
        name: Nom de l'APK (sans extension .apk).

    Returns:
        True si supprime, False si non trouve.
    """
    apk_file = APK_DIR / f"{name}.apk"
    if not apk_file.exists():
        return False
    apk_file.unlink()
    meta_file = _meta_path(apk_file)
    if meta_file.exists():
        meta_file.unlink()
    return True


async def get_apk_path(name: str) -> Path | None:
    """Retourne le chemin complet vers un fichier APK.

    Args:
        name: Nom de l'APK (sans extension .apk).

    Returns:
        Path du fichier APK si existe, None sinon.
    """
    apk_file = APK_DIR / f"{name}.apk"
    if not apk_file.exists():
        return None
    return apk_file
