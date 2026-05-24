"""Tests unitaires pour le module apk."""

import pytest

from src.models import APKInfo


@pytest.mark.asyncio
async def test_apk_info_schema() -> None:
    """Test que le schema APKInfo fonctionne."""
    info = APKInfo(
        name="TestApp",
        filename="testapp.apk",
        version="1.0.0",
        size_bytes=5242880,
        description="Test application",
        uploaded_at="2024-01-01T00:00:00Z",
        checksum_sha256="abc123def456",
    )
    assert info.name == "TestApp"
    assert info.version == "1.0.0"
    assert info.size_bytes == 5242880


@pytest.mark.asyncio
async def test_apk_info_fields() -> None:
    """Test que tous les champs d'APKInfo sont presents."""
    info = APKInfo(
        name="App",
        filename="app.apk",
        version="2.0",
        size_bytes=1000000,
        description="Test",
        uploaded_at="2024-01-01T00:00:00Z",
        checksum_sha256="xyz789",
    )
    assert hasattr(info, "name")
    assert hasattr(info, "filename")
    assert hasattr(info, "version")
    assert hasattr(info, "size_bytes")
    assert hasattr(info, "description")
    assert hasattr(info, "uploaded_at")
    assert hasattr(info, "checksum_sha256")
