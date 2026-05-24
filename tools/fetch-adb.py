"""Telecharge Android platform-tools (adb, fastboot) dans tools/adb/.

Usage:
    python tools/fetch-adb.py            # detecte l'OS courant
    python tools/fetch-adb.py windows    # force une plateforme
    python tools/fetch-adb.py linux
    python tools/fetch-adb.py darwin
    python tools/fetch-adb.py --all      # toutes les plateformes
"""

from __future__ import annotations

import argparse
import io
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

PLATFORMS = ("windows", "linux", "darwin")
BASE_URL = "https://dl.google.com/android/repository/platform-tools-latest-{platform}.zip"
TOOLS_DIR = Path(__file__).resolve().parent
ADB_DIR = TOOLS_DIR / "adb"


def detect_platform() -> str:
    """Detecte la plateforme courante au format Google."""
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform.startswith("linux"):
        return "linux"
    if sys.platform == "darwin":
        return "darwin"
    raise RuntimeError(f"Plateforme non supportee: {sys.platform}")


def fetch_platform(platform: str) -> Path:
    """Telecharge et extrait platform-tools pour une plateforme.

    Args:
        platform: "windows", "linux" ou "darwin".

    Returns:
        Chemin du dossier extrait (tools/adb/{platform}/).
    """
    if platform not in PLATFORMS:
        raise ValueError(f"Plateforme invalide: {platform} (attendu: {PLATFORMS})")

    url = BASE_URL.format(platform=platform)
    target = ADB_DIR / platform

    if target.exists():
        print(f"[skip] {target} existe deja - supprime-le pour re-telecharger")
        return target

    ADB_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[get] {url}")
    with urllib.request.urlopen(url) as response:
        data = response.read()
    print(f"[ok ] {len(data) // 1024} KiB telecharges")

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        zf.extractall(ADB_DIR)

    extracted = ADB_DIR / "platform-tools"
    if not extracted.exists():
        raise RuntimeError("Archive inattendue: pas de dossier platform-tools/")
    shutil.move(str(extracted), str(target))
    print(f"[ok ] extrait dans {target}")
    return target


def main() -> int:
    """Point d'entree CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "platform",
        nargs="?",
        choices=PLATFORMS,
        help="Plateforme cible (defaut: OS courant)",
    )
    parser.add_argument("--all", action="store_true", help="Toutes les plateformes")
    args = parser.parse_args()

    targets = PLATFORMS if args.all else (args.platform or detect_platform(),)
    for platform in targets:
        fetch_platform(platform)
    return 0


if __name__ == "__main__":
    sys.exit(main())
