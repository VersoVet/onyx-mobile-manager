# tools/

Outils tiers utilises par `onyx-mobile-manager` (non versionnes dans git).

## adb / Android platform-tools

Le client GUI (PyQt6) utilise `adb` pour parler aux appareils Android :
configuration VPN, install APK, reboot, etc. (cf. `gui/services/adb_service.py`).

### Recuperer les binaires

```bash
# OS courant (auto-detecte)
python tools/fetch-adb.py

# Plateforme specifique
python tools/fetch-adb.py windows
python tools/fetch-adb.py linux
python tools/fetch-adb.py darwin

# Toutes
python tools/fetch-adb.py --all
```

Apres execution, les binaires sont dans `tools/adb/{platform}/` :

```
tools/adb/
├── windows/   # adb.exe, fastboot.exe, *.dll
├── linux/     # adb, fastboot
└── darwin/    # adb, fastboot
```

### Source

`https://dl.google.com/android/repository/platform-tools-latest-{platform}.zip`

Maintenu par Google (Android SDK Platform-Tools). Toujours derniere version.

### Note git

`tools/adb/` est exclu via `.gitignore` (binaires lourds, telechargeables a la demande).
Seuls `tools/fetch-adb.py` et ce README sont versionnes.
