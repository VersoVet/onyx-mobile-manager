# API - Onyx Mobile Manager

Backend API FastAPI déployée sur **OnyxSoma (10.0.0.44:8095)**.

## Base URL
```
http://10.0.0.44:8095
```

## Health & Status

### GET /health
Vérifie la santé du service.

```bash
curl http://10.0.0.44:8095/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### GET /status
Retourne le statut détaillé avec info SDK.

```bash
curl http://10.0.0.44:8095/status
```

**Response:**
```json
{
  "skill": "onyx-mobile-manager",
  "version": "1.0.0",
  "sdk_connected": true,
  "brain_area": "cerebellum"
}
```

### GET /
Endpoint racine (informations de base).

```bash
curl http://10.0.0.44:8095/
```

---

## Appareils

Gestion du registre d'appareils Android (phones/tablets).

### GET /api/devices
Liste tous les appareils enregistrés.

```bash
curl http://10.0.0.44:8095/api/devices
```

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Pixel 8",
    "device_type": "phone",
    "model": "Google Pixel 8",
    "serial": "ABCD1234",
    "ip_address": "192.168.1.100",
    "adb_port": 5555,
    "status": "online",
    "notes": "Device in lab",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

### POST /api/devices
Enregistre un nouvel appareil.

```bash
curl -X POST http://10.0.0.44:8095/api/devices \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Pixel 8",
    "device_type": "phone",
    "model": "Google Pixel 8",
    "serial": "ABCD1234",
    "ip_address": "192.168.1.100",
    "adb_port": 5555,
    "notes": "Device in lab"
  }'
```

**Fields:**
- `name` (required): Nom de l'appareil
- `device_type` (optional): `phone` ou `tablet` (défaut: phone)
- `model` (optional): Modèle
- `serial` (optional): Numéro de série ADB
- `ip_address` (optional): Adresse IP
- `adb_port` (optional): Port ADB (défaut: 5555)
- `notes` (optional): Notes libres

### GET /api/devices/{id}
Récupère un appareil par ID.

```bash
curl http://10.0.0.44:8095/api/devices/550e8400-e29b-41d4-a716-446655440000
```

### PUT /api/devices/{id}
Modifie un appareil (tous les champs optionnels).

```bash
curl -X PUT http://10.0.0.44:8095/api/devices/{id} \
  -H 'Content-Type: application/json' \
  -d '{"name":"Pixel 8 Pro","status":"maintenance"}'
```

### DELETE /api/devices/{id}
Supprime un appareil du registre.

```bash
curl -X DELETE http://10.0.0.44:8095/api/devices/{id}
```

### PATCH /api/devices/{id}/status
Met à jour le statut d'un appareil.

```bash
curl -X PATCH http://10.0.0.44:8095/api/devices/{id}/status \
  -H 'Content-Type: application/json' \
  -d '{"status":"online"}'
```

**Statuts valides:** `online`, `offline`, `maintenance`

---

## Historique

Audit trail de toutes les actions sur les appareils.

### GET /api/history
Récupère l'historique avec filtres optionnels.

```bash
curl "http://10.0.0.44:8095/api/history?device_id=xxx&action=apk_install&limit=50"
```

**Query parameters:**
- `device_id` (optional): Filtrer par appareil
- `action` (optional): Filtrer par type d'action
- `operator` (optional): Filtrer par opérateur
- `success` (optional): true/false pour succès/échec
- `since` (optional): ISO 8601 date (ex: 2024-01-01T00:00:00Z)
- `until` (optional): ISO 8601 date
- `limit` (optional): Nombre de résultats (défaut: 100, max: 1000)
- `offset` (optional): Pagination (défaut: 0)

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "device_id": "550e8400-e29b-41d4-a716-446655440000",
    "device_name": "Pixel 8",
    "action": "apk_install",
    "details": "Installed onyx-dashboard v1.2.0",
    "operator": "admin",
    "success": true,
    "timestamp": "2024-01-15T10:30:00Z"
  }
]
```

### GET /api/history/{device_id}
Récupère l'historique d'un appareil spécifique.

```bash
curl http://10.0.0.44:8095/api/history/550e8400-e29b-41d4-a716-446655440000
```

### POST /api/history
Enregistre une action dans l'historique.

```bash
curl -X POST http://10.0.0.44:8095/api/history \
  -H 'Content-Type: application/json' \
  -d '{
    "device_id": "550e8400-e29b-41d4-a716-446655440000",
    "action": "apk_install",
    "details": "Installed app v1.0",
    "operator": "admin",
    "success": true
  }'
```

**Fields:**
- `device_id` (required): ID de l'appareil concerné
- `action` (required): Type d'action (voir list ci-dessous)
- `details` (optional): Description détaillée
- `operator` (optional): Qui a effectué l'action (défaut: "system")
- `success` (optional): true/false (défaut: true)

**Types d'action valides:**
`apk_install`, `apk_uninstall`, `apk_update`, `vpn_configure`, `vpn_remove`, `adb_connect`, `adb_disconnect`, `config_push`, `shell_command`, `reboot`, `device_register`, `device_remove`, `other`

### GET /api/history/export
Exporte l'historique en format JSON ou CSV.

```bash
# JSON
curl "http://10.0.0.44:8095/api/history/export?format=json" > history.json

# CSV
curl "http://10.0.0.44:8095/api/history/export?format=csv" > history.csv
```

---

## APKs

Gestion et distribution de packages APK.

### GET /api/apk
Liste tous les APKs disponibles.

```bash
curl http://10.0.0.44:8095/api/apk
```

**Response:**
```json
[
  {
    "name": "onyx-dashboard",
    "filename": "onyx-dashboard.apk",
    "version": "1.2.0",
    "size_bytes": 5242880,
    "description": "Dashboard Onyx pour gestion centralisée",
    "uploaded_at": "2024-01-15T10:30:00Z",
    "checksum_sha256": "abc123def456..."
  }
]
```

### POST /api/apk/upload
Upload un nouvel APK.

```bash
curl -X POST http://10.0.0.44:8095/api/apk/upload \
  -F "file=@onyx-dashboard.apk" \
  -F "version=1.2.0" \
  -F "description=Dashboard Onyx"
```

**Form fields:**
- `file` (required): Fichier APK (multipart)
- `version` (required): Numéro de version (ex: 1.2.0)
- `description` (optional): Description de l'APK

### GET /api/apk/{name}/download
Télécharge un APK par son nom.

```bash
curl -o app.apk http://10.0.0.44:8095/api/apk/onyx-dashboard/download
```

**Parameters:**
- `name` (required): Nom de l'APK (sans extension .apk)

### GET /api/apk/{name}/info
Récupère les informations d'un APK.

```bash
curl http://10.0.0.44:8095/api/apk/onyx-dashboard/info
```

### DELETE /api/apk/{name}
Supprime un APK du stockage.

```bash
curl -X DELETE http://10.0.0.44:8095/api/apk/onyx-dashboard
```

---

## Erreurs

Codes HTTP utilisés:
- `200 OK`: Succès
- `201 Created`: Ressource créée
- `400 Bad Request`: Erreur de validation
- `404 Not Found`: Ressource non trouvée
- `500 Internal Server Error`: Erreur serveur

**Response d'erreur:**
```json
{
  "detail": "Description de l'erreur"
}
```

---

## OpenAPI/Swagger

Documentation interactive disponible à:
```
http://10.0.0.44:8095/docs
```
