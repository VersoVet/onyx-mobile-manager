"""Routes FastAPI pour la gestion des appareils mobiles."""

from fastapi import APIRouter, HTTPException

from src.models import Device, DeviceCreate, DeviceUpdate, StatusUpdate
from src.modules.devices.service import (
    create_device,
    delete_device,
    get_device,
    get_devices,
    update_device,
    update_device_status,
)

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.get("/", response_model=list[Device])
async def list_devices() -> list[Device]:
    """Liste tous les appareils enregistres.

    Returns:
        Liste de tous les appareils tries par date de creation.
    """
    return await get_devices()


@router.post("/", response_model=Device, status_code=201)
async def register_device(data: DeviceCreate) -> Device:
    """Enregistre un nouvel appareil.

    Args:
        data: Donnees de creation de l'appareil.

    Returns:
        L'appareil cree avec son ID genere.
    """
    return await create_device(data)


@router.get("/{device_id}", response_model=Device)
async def read_device(device_id: str) -> Device:
    """Recupere un appareil par son identifiant.

    Args:
        device_id: UUID de l'appareil.

    Returns:
        L'appareil correspondant.

    Raises:
        HTTPException: 404 si l'appareil n'existe pas.
    """
    device = await get_device(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.put("/{device_id}", response_model=Device)
async def modify_device(device_id: str, data: DeviceUpdate) -> Device:
    """Met a jour un appareil existant.

    Args:
        device_id: UUID de l'appareil a modifier.
        data: Champs a mettre a jour.

    Returns:
        L'appareil mis a jour.

    Raises:
        HTTPException: 404 si l'appareil n'existe pas.
    """
    device = await update_device(device_id, data)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.delete("/{device_id}", status_code=204)
async def remove_device(device_id: str) -> None:
    """Supprime un appareil.

    Args:
        device_id: UUID de l'appareil a supprimer.

    Raises:
        HTTPException: 404 si l'appareil n'existe pas.
    """
    deleted = await delete_device(device_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Device not found")


@router.patch("/{device_id}/status", response_model=Device)
async def change_device_status(device_id: str, data: StatusUpdate) -> Device:
    """Met a jour le statut d'un appareil.

    Args:
        device_id: UUID de l'appareil.
        data: Nouveau statut a appliquer.

    Returns:
        L'appareil avec le statut mis a jour.

    Raises:
        HTTPException: 404 si l'appareil n'existe pas.
    """
    device = await update_device_status(device_id, data)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device
