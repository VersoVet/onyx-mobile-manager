"""Service CRUD pour la gestion des appareils mobiles en SQLite."""

import uuid
from datetime import datetime, timezone

import aiosqlite

from src.config import DB_PATH
from src.models import Device, DeviceCreate, DeviceStatus, DeviceUpdate, StatusUpdate

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS devices (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    device_type TEXT NOT NULL DEFAULT 'phone',
    model TEXT DEFAULT '',
    serial TEXT DEFAULT '',
    ip_address TEXT DEFAULT '',
    adb_port INTEGER DEFAULT 5555,
    status TEXT DEFAULT 'offline',
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""


def _now() -> str:
    """Retourne le timestamp ISO 8601 courant en UTC."""
    return datetime.now(timezone.utc).isoformat()


def _row_to_device(row: aiosqlite.Row) -> Device:
    """Convertit une ligne SQLite en modele Device."""
    return Device(**{k: row[k] for k in Device.model_fields})


async def init_db() -> None:
    """Initialise la base de donnees et cree la table devices si absente.

    Cree le repertoire parent de DB_PATH si necessaire.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.execute(CREATE_TABLE_SQL)
        await db.commit()


async def create_device(data: DeviceCreate) -> Device:
    """Enregistre un nouvel appareil dans la base.

    Args:
        data: Donnees de creation (nom, type, modele, etc.).

    Returns:
        L'appareil cree avec son ID et ses timestamps.
    """
    device_id = str(uuid.uuid4())
    now = _now()
    async with aiosqlite.connect(str(DB_PATH)) as db:
        db.row_factory = aiosqlite.Row
        await db.execute(
            """INSERT INTO devices
               (id, name, device_type, model, serial, ip_address, adb_port, status, notes, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                device_id,
                data.name,
                data.device_type.value,
                data.model,
                data.serial,
                data.ip_address,
                data.adb_port,
                DeviceStatus.OFFLINE.value,
                data.notes,
                now,
                now,
            ),
        )
        await db.commit()
        cursor = await db.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        row = await cursor.fetchone()
    return _row_to_device(row)  # type: ignore[arg-type]


async def get_devices() -> list[Device]:
    """Recupere tous les appareils enregistres.

    Returns:
        Liste de tous les appareils tries par date de creation.
    """
    async with aiosqlite.connect(str(DB_PATH)) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM devices ORDER BY created_at DESC")
        rows = await cursor.fetchall()
    return [_row_to_device(row) for row in rows]


async def get_device(device_id: str) -> Device | None:
    """Recupere un appareil par son identifiant.

    Args:
        device_id: UUID de l'appareil.

    Returns:
        L'appareil trouve ou None si inexistant.
    """
    async with aiosqlite.connect(str(DB_PATH)) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        row = await cursor.fetchone()
    if row is None:
        return None
    return _row_to_device(row)


async def update_device(device_id: str, data: DeviceUpdate) -> Device | None:
    """Met a jour les champs d'un appareil existant.

    Args:
        device_id: UUID de l'appareil a modifier.
        data: Champs a mettre a jour (seuls les non-None sont appliques).

    Returns:
        L'appareil mis a jour ou None si inexistant.
    """
    updates = data.model_dump(exclude_none=True)
    if not updates:
        return await get_device(device_id)

    # Convertir l'enum en valeur string si present
    if "device_type" in updates:
        updates["device_type"] = updates["device_type"].value

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values())
    values.append(_now())
    values.append(device_id)

    async with aiosqlite.connect(str(DB_PATH)) as db:
        db.row_factory = aiosqlite.Row
        await db.execute(
            f"UPDATE devices SET {set_clause}, updated_at = ? WHERE id = ?",  # noqa: S608
            values,
        )
        await db.commit()
        cursor = await db.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        row = await cursor.fetchone()
    if row is None:
        return None
    return _row_to_device(row)


async def delete_device(device_id: str) -> bool:
    """Supprime un appareil de la base.

    Args:
        device_id: UUID de l'appareil a supprimer.

    Returns:
        True si l'appareil a ete supprime, False si inexistant.
    """
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute("DELETE FROM devices WHERE id = ?", (device_id,))
        await db.commit()
        return cursor.rowcount > 0


async def update_device_status(device_id: str, data: StatusUpdate) -> Device | None:
    """Met a jour uniquement le statut d'un appareil.

    Args:
        device_id: UUID de l'appareil.
        data: Nouveau statut a appliquer.

    Returns:
        L'appareil mis a jour ou None si inexistant.
    """
    async with aiosqlite.connect(str(DB_PATH)) as db:
        db.row_factory = aiosqlite.Row
        await db.execute(
            "UPDATE devices SET status = ?, updated_at = ? WHERE id = ?",
            (data.status.value, _now(), device_id),
        )
        await db.commit()
        cursor = await db.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        row = await cursor.fetchone()
    if row is None:
        return None
    return _row_to_device(row)
