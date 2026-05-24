# Architecture - Onyx Mobile Manager

## Vue d'ensemble

Architecture hybride: backend API centralisé + client GUI desktop.

```
┌─────────────────────────────┐     ┌─────────────────────────────┐
│  GUI Client (PyQt6)         │     │  Backend API (FastAPI)      │
│  Windows / Linux            │────▶│  OnyxSoma:8095              │
│                             │HTTP │                             │
│  - Gestion appareils        │     │  - CRUD appareils           │
│  - Config VPN via ADB       │     │  - Audit trail historique   │
│  - Install APK via ADB      │     │  - Gestion stockage APKs    │
│  - Consultation historique  │     │  - Health check + métriques │
└──────────┬──────────────────┘     └─────────────────────────────┘
           │ ADB
           ▼
    ┌──────────────────┐
    │  Appareils Android│
    │ (Phones/Tablets) │
    └──────────────────┘
```

## Structure du code

```
onyx-mobile-manager/
├── src/                       # Backend FastAPI
│   ├── main.py               # Point d'entrée, routers, lifespan
│   ├── config.py             # Configuration (paths, port, version)
│   ├── models.py             # Modèles Pydantic partagés
│   └── modules/              # 3 modules métier
│       ├── devices/          # CRUD appareils SQLite
│       │   ├── service.py    # Logique métier (init_db, CRUD)
│       │   ├── routes.py     # Endpoints FastAPI
│       │   └── tests/        # Tests unitaires
│       ├── history/          # Audit trail SQLite
│       │   ├── service.py    # Logique métier (log_action, get_history)
│       │   ├── routes.py     # Endpoints FastAPI
│       │   └── tests/        # Tests unitaires
│       └── apk/              # Stockage APKs
│           ├── service.py    # Logique métier (save_apk, list_apks)
│           ├── routes.py     # Endpoints FastAPI (upload, download)
│           └── tests/        # Tests unitaires
│
├── gui/                       # Client PyQt6 (optionnel)
│   ├── app.py               # Entry point PyQt6
│   ├── main_window.py       # Fenêtre principale
│   ├── widgets/             # 4 panels UI
│   │   ├── device_panel.py  # Gestion appareils
│   │   ├── vpn_panel.py     # Configuration VPN
│   │   ├── apk_panel.py     # Gestion APKs
│   │   └── history_panel.py # Historique
│   └── services/            # Logique client
│       ├── api_client.py    # Client HTTP → backend
│       ├── adb_service.py   # Wrapper ADB
│       └── vpn_service.py   # Gestion WireGuard
│
├── tests/                     # Tests d'intégration
│   ├── conftest.py          # Fixtures pytest
│   └── test_integration.py  # Scénarios complets
│
├── manifest.json            # Configuration Forge
├── requirements.txt         # Dépendances Python
├── requirements-gui.txt     # Dépendances PyQt6 (optionnel)
├── ARCHITECTURE.md          # Ce fichier
├── API.md                   # Documentation API REST
├── TODO.md                  # Tâches en cours/futures
└── .gitignore              # Patterns d'exclusion git
```

## Modules métier

### Devices (Port d'entrée principal)
- **Modèles**: `Device`, `DeviceCreate`, `DeviceUpdate`, `DeviceStatus`
- **Statuts**: ONLINE, OFFLINE, MAINTENANCE
- **CRUD**: create_device, get_devices, get_device, update_device, delete_device
- **Base**: SQLite (`devices` table)

### History (Audit trail)
- **Modèles**: `HistoryEntry`, `HistoryCreate`, `HistoryFilter`, `ActionType`
- **Types d'action**: APK_INSTALL, VPN_CONFIGURE, REBOOT, etc. (12 types)
- **Requêtes**: log_action, get_history (avec filtres), get_device_history
- **Base**: SQLite (`history` table avec indexes sur device_id, action, timestamp)

### APK (Gestion de packages)
- **Modèles**: `APKInfo`
- **Stockage**: Fichiers `.apk` + métadonnées JSON sidecar (`.apk.meta.json`)
- **Opérations**: save_apk, list_apks, get_apk_info, delete_apk, get_apk_path
- **Checksum**: SHA256 stocké dans métadonnées

## Stockage persistant

| Ressource | Type | Localisation | Notes |
|-----------|------|--------------|-------|
| **Appareils** | SQLite | `/opt/onyx/data/mobile-manager/mobile-manager.db` | Table `devices` |
| **Historique** | SQLite | `/opt/onyx/data/mobile-manager/mobile-manager.db` | Table `history` avec 3 indexes |
| **APKs** | Fichiers | `/opt/onyx/data/mobile-manager/apks/` | `.apk` + `.apk.meta.json` |

## Technologies

| Composant | Tech | Raison |
|-----------|------|--------|
| **API** | FastAPI + uvicorn | Async, type-safe, auto-docs OpenAPI |
| **BD** | SQLite + aiosqlite | Lightweight, async, pas de serveur |
| **HTTP** | httpx async | Async client pour requêtes API internes |
| **Validation** | Pydantic v2 | Type-safe request/response models |
| **Tests** | pytest + pytest-asyncio | Framework async pour tests |
| **Lint** | ruff + mypy strict | Type checking strict, code quality |
| **GUI** | PyQt6 (optionnel) | Desktop client pour gestion locale |

## Points clés

1. **Imports absolus**: `from src.xxx import` (jamais de relatifs)
2. **Types strict**: Tous les params/returns annotés (mypy --strict)
3. **Async throughout**: aiosqlite, httpx, FastAPI (pas de bloquant)
4. **Modules autonomes**: Pas de dépendances circulaires (devices → history possible)
5. **Tests modulaires**: `src/modules/{nom}/tests/test_{nom}.py`
6. **Docstrings Google**: Convention obligatoire (80%+ couverture)
