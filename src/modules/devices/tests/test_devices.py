"""Tests unitaires pour le module devices."""

import pytest

from src.models import DeviceCreate, DeviceType


@pytest.mark.asyncio
async def test_device_create_schema() -> None:
    """Test que le schema DeviceCreate fonctionne."""
    data = DeviceCreate(
        name="Test Phone",
        device_type=DeviceType.PHONE,
        model="Samsung Galaxy",
    )
    assert data.name == "Test Phone"
    assert data.device_type == DeviceType.PHONE


@pytest.mark.asyncio
async def test_device_types() -> None:
    """Test que les types d'appareil sont valides."""
    assert DeviceType.PHONE.value == "phone"
    assert DeviceType.TABLET.value == "tablet"


@pytest.mark.asyncio
async def test_device_create_defaults() -> None:
    """Test que les valeurs par defaut sont correctes."""
    data = DeviceCreate(name="Default Device")
    assert data.adb_port == 5555
    assert data.model == ""
    assert data.notes == ""
