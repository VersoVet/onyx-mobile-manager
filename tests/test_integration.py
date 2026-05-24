"""Tests d'integration pour onyx-mobile-manager."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture(autouse=True)
def _setup_test_db(tmp_path, monkeypatch):
    """Configure une base temporaire pour les tests."""
    test_db = tmp_path / "test.db"
    test_apk_dir = tmp_path / "apks"
    monkeypatch.setattr("src.config.DB_PATH", test_db)
    monkeypatch.setattr("src.config.APK_DIR", test_apk_dir)
    monkeypatch.setattr("src.config.DATA_DIR", tmp_path)
    monkeypatch.setattr("src.modules.devices.service.DB_PATH", test_db)
    monkeypatch.setattr("src.modules.history.service.DB_PATH", test_db)
    monkeypatch.setattr("src.modules.apk.service.APK_DIR", test_apk_dir)


@pytest.fixture
def client():
    """Client de test FastAPI."""
    with TestClient(app) as c:
        yield c


def test_health(client):
    """Verifie que /health repond correctement."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_root(client):
    """Verifie que / retourne les infos de base."""
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["service"] == "onyx-mobile-manager"


def test_device_crud(client):
    """Teste le cycle complet CRUD d'un appareil."""
    # Create
    r = client.post(
        "/api/devices",
        json={
            "name": "Test Phone",
            "device_type": "phone",
            "model": "Pixel 8",
            "serial": "ABCD1234",
            "ip_address": "192.168.1.100",
        },
    )
    assert r.status_code == 201
    device = r.json()
    device_id = device["id"]
    assert device["name"] == "Test Phone"
    assert device["status"] == "offline"

    # Read
    r = client.get(f"/api/devices/{device_id}")
    assert r.status_code == 200
    assert r.json()["serial"] == "ABCD1234"

    # Update
    r = client.put(f"/api/devices/{device_id}", json={"name": "Updated Phone"})
    assert r.status_code == 200
    assert r.json()["name"] == "Updated Phone"

    # Status
    r = client.patch(f"/api/devices/{device_id}/status", json={"status": "online"})
    assert r.status_code == 200
    assert r.json()["status"] == "online"

    # List
    r = client.get("/api/devices")
    assert r.status_code == 200
    assert len(r.json()) == 1

    # Delete
    r = client.delete(f"/api/devices/{device_id}")
    assert r.status_code == 204


def test_device_not_found(client):
    """Verifie le 404 sur un appareil inexistant."""
    r = client.get("/api/devices/nonexistent")
    assert r.status_code == 404


def test_history_log_and_query(client):
    """Teste l'enregistrement et la consultation de l'historique."""
    # Create device first
    r = client.post("/api/devices", json={"name": "History Test"})
    device_id = r.json()["id"]

    # Log action
    r = client.post(
        "/api/history",
        json={
            "device_id": device_id,
            "action": "apk_install",
            "details": "Installed onyx-dashboard v1.0",
            "operator": "test",
        },
    )
    assert r.status_code == 201
    entry = r.json()
    assert entry["action"] == "apk_install"
    assert entry["device_name"] == "History Test"

    # Query history
    r = client.get("/api/history")
    assert r.status_code == 200
    assert len(r.json()) >= 1

    # Device history
    r = client.get(f"/api/history/{device_id}")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_history_export_json(client):
    """Teste l'export JSON de l'historique."""
    r = client.get("/api/history/export?format=json")
    assert r.status_code == 200


def test_history_export_csv(client):
    """Teste l'export CSV de l'historique."""
    r = client.get("/api/history/export?format=csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")


def test_apk_list_empty(client):
    """Verifie que la liste APK est vide au depart."""
    r = client.get("/api/apk")
    assert r.status_code == 200
    assert r.json() == []
