"""Point d'entree FastAPI pour onyx-mobile-manager."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import PORT, SKILL_NAME, VERSION
from src.modules.apk.routes import router as apk_router
from src.modules.apk.service import init_storage
from src.modules.devices.routes import router as devices_router
from src.modules.devices.service import init_db as init_devices_db
from src.modules.history.routes import router as history_router
from src.modules.history.service import init_db as init_history_db

try:
    from onyx_sdk import OnyxClient, SkillStatus

    HAS_SDK = True
except ImportError:
    HAS_SDK = False
    OnyxClient = None
    SkillStatus = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(SKILL_NAME)

onyx: OnyxClient | None = None


def signal_working(message: str = "processing") -> None:
    """Signale un traitement en cours au dashboard.

    Args:
        message: Description du traitement.
    """
    if onyx and HAS_SDK:
        onyx.status(SkillStatus.WORKING, message)


def signal_up() -> None:
    """Signale que le skill est operationnel."""
    if onyx and HAS_SDK:
        onyx.status(SkillStatus.UP)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gere le cycle de vie de l'application.

    Initialise la base de donnees, le stockage APK et le SDK Onyx au demarrage.
    Arrete le SDK proprement a la fermeture.

    Args:
        app: Instance FastAPI.

    Yields:
        None pendant la duree de vie de l'application.
    """
    global onyx
    logger.info("Demarrage %s v%s sur port %d", SKILL_NAME, VERSION, PORT)

    await init_devices_db()
    await init_history_db()
    await init_storage()
    logger.info("Base de donnees et stockage initialises")

    if HAS_SDK:
        onyx = OnyxClient(SKILL_NAME, "cerebellum", port=PORT)
        onyx.start()  # Publie UP + heartbeat
        logger.info("OnyxSDK connecte")

    yield

    if onyx:
        onyx.status(SkillStatus.DOWN)
        onyx.stop()  # Publie DOWN + arret heartbeat
    logger.info("Arret %s", SKILL_NAME)


app = FastAPI(
    title="Onyx Mobile Manager",
    description="Gestion et configuration de telephones/tablettes Android pour Onyx",
    version=VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(devices_router)
app.include_router(history_router)
app.include_router(apk_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Verifie la sante du service.

    Returns:
        Statut et version du service.
    """
    return {"status": "healthy", "version": VERSION}


@app.get("/")
async def root() -> dict[str, str]:
    """Endpoint racine.

    Returns:
        Informations de base du service.
    """
    return {
        "service": SKILL_NAME,
        "version": VERSION,
        "status": "running",
    }


@app.get("/status")
async def status() -> dict[str, str | bool]:
    """Retourne le statut detaille du service.

    Returns:
        Informations de statut incluant la connexion SDK.
    """
    return {
        "skill": SKILL_NAME,
        "version": VERSION,
        "sdk_connected": HAS_SDK and onyx is not None,
        "brain_area": "cerebellum",
    }


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=PORT, reload=True)
