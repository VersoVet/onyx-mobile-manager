"""Configuration pytest pour les tests d'intégration."""

import pytest


@pytest.fixture(scope="session")
def event_loop():
    """Fixture pour l'event loop pytest-asyncio."""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def pytest_configure(config):
    """Configure pytest avec les marqueurs asynchrones."""
    config.addinivalue_line(
        "markers", "asyncio: marque un test comme asynchrone (pytest-asyncio)"
    )
