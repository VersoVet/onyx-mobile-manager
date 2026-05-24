"""Modeles Pydantic partages pour le backend."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DeviceType(str, Enum):
    """Type d'appareil mobile."""

    PHONE = "phone"
    TABLET = "tablet"


class DeviceStatus(str, Enum):
    """Statut de connexion d'un appareil."""

    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class DeviceCreate(BaseModel):
    """Schema de creation d'un appareil."""

    name: str = Field(
        ..., min_length=1, max_length=100, description="Nom de l'appareil"
    )
    device_type: DeviceType = Field(
        default=DeviceType.PHONE, description="Type d'appareil"
    )
    model: str = Field(default="", description="Modele (ex: Samsung Galaxy S24)")
    serial: str = Field(default="", description="Numero de serie ADB")
    ip_address: str = Field(default="", description="Adresse IP sur le reseau")
    adb_port: int = Field(default=5555, description="Port ADB WiFi")
    notes: str = Field(default="", description="Notes libres")


class DeviceUpdate(BaseModel):
    """Schema de modification d'un appareil."""

    name: str | None = None
    device_type: DeviceType | None = None
    model: str | None = None
    serial: str | None = None
    ip_address: str | None = None
    adb_port: int | None = None
    notes: str | None = None


class Device(BaseModel):
    """Appareil complet avec metadonnees."""

    id: str
    name: str
    device_type: DeviceType
    model: str
    serial: str
    ip_address: str
    adb_port: int
    status: DeviceStatus
    notes: str
    created_at: str
    updated_at: str


class StatusUpdate(BaseModel):
    """Mise a jour du statut d'un appareil."""

    status: DeviceStatus


class ActionType(str, Enum):
    """Type d'action loggee dans l'historique."""

    APK_INSTALL = "apk_install"
    APK_UNINSTALL = "apk_uninstall"
    APK_UPDATE = "apk_update"
    VPN_CONFIGURE = "vpn_configure"
    VPN_REMOVE = "vpn_remove"
    ADB_CONNECT = "adb_connect"
    ADB_DISCONNECT = "adb_disconnect"
    CONFIG_PUSH = "config_push"
    SHELL_COMMAND = "shell_command"
    REBOOT = "reboot"
    DEVICE_REGISTER = "device_register"
    DEVICE_REMOVE = "device_remove"
    OTHER = "other"


class HistoryCreate(BaseModel):
    """Schema pour logger une action."""

    device_id: str = Field(..., description="ID de l'appareil concerne")
    action: ActionType = Field(..., description="Type d'action")
    details: str = Field(default="", description="Details de l'action")
    operator: str = Field(default="system", description="Qui a fait l'action")
    success: bool = Field(default=True, description="Succes ou echec")


class HistoryEntry(BaseModel):
    """Entree d'historique complete."""

    id: str
    device_id: str
    device_name: str
    action: ActionType
    details: str
    operator: str
    success: bool
    timestamp: str


class HistoryFilter(BaseModel):
    """Filtres pour requeter l'historique."""

    device_id: str | None = None
    action: ActionType | None = None
    operator: str | None = None
    success: bool | None = None
    since: datetime | None = None
    until: datetime | None = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class APKInfo(BaseModel):
    """Informations sur un APK stocke."""

    name: str
    filename: str
    version: str
    size_bytes: int
    description: str
    uploaded_at: str
    checksum_sha256: str
