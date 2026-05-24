"""Tests unitaires pour le module history."""

import pytest

from src.models import ActionType, HistoryCreate, HistoryFilter


@pytest.mark.asyncio
async def test_history_create_schema() -> None:
    """Test que le schema HistoryCreate fonctionne."""
    data = HistoryCreate(
        device_id="device-123",
        action=ActionType.APK_INSTALL,
        details="Installed v1.0",
    )
    assert data.device_id == "device-123"
    assert data.action == ActionType.APK_INSTALL


@pytest.mark.asyncio
async def test_action_types() -> None:
    """Test que les types d'action sont valides."""
    assert ActionType.APK_INSTALL.value == "apk_install"
    assert ActionType.VPN_CONFIGURE.value == "vpn_configure"
    assert ActionType.REBOOT.value == "reboot"


@pytest.mark.asyncio
async def test_history_filter_defaults() -> None:
    """Test les valeurs par defaut du filtre."""
    filters = HistoryFilter()
    assert filters.limit == 100
    assert filters.offset == 0
    assert filters.device_id is None
