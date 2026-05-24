# Architecture - Onyx Mobile Manager

## Vue d'ensemble

Architecture hybride: backend API centralise + client GUI desktop.

```
┌─────────────────────────────┐     ┌─────────────────────────────┐
│  GUI Client (PyQt6)         │     │  Backend API (FastAPI)      │
│  Windows / Linux            │────▶│  172.16.0.3:8095            │
│                             │HTTP │                             │
│  - Gestion appareils        │     │  - Registre appareils       │
│  - Config VPN via ADB       │     │  - Historique SQLite        │
│  - Install APK via ADB      │     │  - Stockage APKs            │
│  - Historique                │     │                             │
└──────────┬──────────────────┘     └─────────────────────────────┘
           │ ADB
           ▼
    ┌──────────────┐
    │  Telephones   │
    │  Tablettes    │
    └──────────────┘
```

## Composants

### Backend (src/)
- **main.py** - Entry point FastAPI, lifespan, routers
- **config.py** - Configuration (port, paths, version)
- **models.py** - Modeles Pydantic partages
- **modules/devices/** - CRUD appareils SQLite
- **modules/history/** - Audit trail SQLite
- **modules/apk/** - Stockage et versioning APKs

### GUI Client (gui/)
- **app.py** - Entry point PyQt6
- **main_window.py** - Fenetre principale + onglets
- **widgets/** - 4 panels (devices, vpn, apk, history)
- **services/** - API client, ADB wrapper, VPN service

## Stockage
- **SQLite** - Appareils et historique (`/opt/onyx/data/mobile-manager/mobile-manager.db`)
- **Fichiers APK** - Repertoire (`/opt/onyx/data/mobile-manager/apks/`) avec metadata JSON sidecar

## Technologies
- FastAPI + uvicorn (backend)
- PyQt6 (GUI desktop)
- aiosqlite (base de donnees async)
- httpx (HTTP client)
- ADB CLI (gestion appareils Android)
- WireGuard (VPN)
