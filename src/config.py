"""Configuration du backend onyx-mobile-manager."""

import json
import os
from pathlib import Path

SKILL_NAME = "onyx-mobile-manager"
SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", "/opt/onyx/data/mobile-manager"))
APK_DIR = DATA_DIR / "apks"
DB_PATH = DATA_DIR / "mobile-manager.db"
PORT = int(os.getenv("SKILL_PORT", "8095"))


def load_version() -> str:
    """Charge la version depuis manifest.json.

    Returns:
        Version string ou '0.0.0' si indisponible.
    """
    try:
        manifest_path = SKILL_DIR / "manifest.json"
        with open(manifest_path) as f:
            data = json.load(f)
            version: str = data.get("version", "0.0.0")
            return version
    except Exception:
        return "0.0.0"


VERSION = load_version()
