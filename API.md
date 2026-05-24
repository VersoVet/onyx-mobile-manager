# API - Onyx Mobile Manager

Backend API deployee sur 172.16.0.3:8095.

## Health & Status

### GET /health
```bash
curl http://172.16.0.3:8095/health
```
```json
{"status": "healthy", "version": "1.0.0"}
```

### GET /status
```bash
curl http://172.16.0.3:8095/status
```

---

## Appareils

### GET /api/devices
Liste tous les appareils.
```bash
curl http://172.16.0.3:8095/api/devices
```

### POST /api/devices
Enregistre un appareil.
```bash
curl -X POST http://172.16.0.3:8095/api/devices \
  -H 'Content-Type: application/json' \
  -d '{"name":"Pixel 8","device_type":"phone","model":"Google Pixel 8","serial":"ABCD1234","ip_address":"192.168.1.100","adb_port":5555}'
```

### GET /api/devices/{id}
Recupere un appareil par ID.

### PUT /api/devices/{id}
Modifie un appareil.
```bash
curl -X PUT http://172.16.0.3:8095/api/devices/{id} \
  -H 'Content-Type: application/json' \
  -d '{"name":"Pixel 8 Pro"}'
```

### DELETE /api/devices/{id}
Supprime un appareil.

### PATCH /api/devices/{id}/status
Met a jour le statut.
```bash
curl -X PATCH http://172.16.0.3:8095/api/devices/{id}/status \
  -H 'Content-Type: application/json' \
  -d '{"status":"online"}'
```
Statuts valides: `online`, `offline`, `maintenance`

---

## Historique

### GET /api/history
Historique avec filtres.
```bash
curl "http://172.16.0.3:8095/api/history?device_id=xxx&action=apk_install&limit=50"
```
Filtres: `device_id`, `action`, `operator`, `success`, `since`, `until`, `limit`, `offset`

### GET /api/history/{device_id}
Historique d'un appareil.

### POST /api/history
Logge une action.
```bash
curl -X POST http://172.16.0.3:8095/api/history \
  -H 'Content-Type: application/json' \
  -d '{"device_id":"xxx","action":"apk_install","details":"Installed app v1.0","operator":"admin"}'
```
Actions: `apk_install`, `apk_uninstall`, `apk_update`, `vpn_configure`, `vpn_remove`, `adb_connect`, `adb_disconnect`, `config_push`, `shell_command`, `reboot`, `device_register`, `device_remove`, `other`

### GET /api/history/export
Exporte l'historique.
```bash
# JSON
curl "http://172.16.0.3:8095/api/history/export?format=json"

# CSV
curl "http://172.16.0.3:8095/api/history/export?format=csv" -o history.csv
```

---

## APKs

### GET /api/apk
Liste les APKs disponibles.

### POST /api/apk/upload
Upload un APK.
```bash
curl -X POST http://172.16.0.3:8095/api/apk/upload \
  -F "file=@onyx-dashboard.apk" \
  -F "version=1.2.0" \
  -F "description=Dashboard Onyx"
```

### GET /api/apk/{name}/download
Telecharge un APK.
```bash
curl -o app.apk http://172.16.0.3:8095/api/apk/onyx-dashboard/download
```

### GET /api/apk/{name}/info
Informations d'un APK.

### DELETE /api/apk/{name}
Supprime un APK.
