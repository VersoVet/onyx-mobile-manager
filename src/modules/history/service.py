"""Service d'historique et audit trail avec aiosqlite."""

import uuid
from datetime import datetime, timezone

import aiosqlite

from src.config import DB_PATH
from src.models import ActionType, HistoryCreate, HistoryEntry, HistoryFilter

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS history (
    id TEXT PRIMARY KEY,
    device_id TEXT NOT NULL,
    device_name TEXT NOT NULL DEFAULT '',
    action TEXT NOT NULL,
    details TEXT NOT NULL DEFAULT '',
    operator TEXT NOT NULL DEFAULT 'system',
    success INTEGER NOT NULL DEFAULT 1,
    timestamp TEXT NOT NULL
)
"""

CREATE_INDEX_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_history_device_id ON history(device_id)",
    "CREATE INDEX IF NOT EXISTS idx_history_action ON history(action)",
    "CREATE INDEX IF NOT EXISTS idx_history_timestamp ON history(timestamp)",
]


async def init_db() -> None:
    """Initialise la table history dans la base SQLite.

    Cree la table et les index si ils n'existent pas encore.
    """
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.execute(CREATE_TABLE_SQL)
        for sql in CREATE_INDEX_SQL:
            await db.execute(sql)
        await db.commit()


async def _resolve_device_name(db: aiosqlite.Connection, device_id: str) -> str:
    """Recupere le nom d'un appareil depuis la table devices.

    Args:
        db: Connexion aiosqlite active.
        device_id: Identifiant de l'appareil.

    Returns:
        Nom de l'appareil ou chaine vide si introuvable.
    """
    try:
        cursor = await db.execute("SELECT name FROM devices WHERE id = ?", (device_id,))
        row = await cursor.fetchone()
        return row[0] if row else ""
    except Exception:
        return ""


async def log_action(entry: HistoryCreate) -> HistoryEntry:
    """Enregistre une action dans l'historique.

    Args:
        entry: Donnees de l'action a enregistrer.

    Returns:
        Entree d'historique complete avec id et timestamp generes.
    """
    entry_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    async with aiosqlite.connect(str(DB_PATH)) as db:
        device_name = await _resolve_device_name(db, entry.device_id)

        await db.execute(
            """INSERT INTO history
               (id, device_id, device_name, action, details, operator, success, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                entry_id,
                entry.device_id,
                device_name,
                entry.action.value,
                entry.details,
                entry.operator,
                1 if entry.success else 0,
                timestamp,
            ),
        )
        await db.commit()

    return HistoryEntry(
        id=entry_id,
        device_id=entry.device_id,
        device_name=device_name,
        action=entry.action,
        details=entry.details,
        operator=entry.operator,
        success=entry.success,
        timestamp=timestamp,
    )


async def get_history(filters: HistoryFilter) -> list[HistoryEntry]:
    """Recupere l'historique avec filtres optionnels.

    Args:
        filters: Criteres de filtrage (device_id, action, dates, etc.).

    Returns:
        Liste d'entrees d'historique correspondant aux filtres.
    """
    query = "SELECT id, device_id, device_name, action, details, operator, success, timestamp FROM history WHERE 1=1"
    params: list[str | int] = []

    if filters.device_id is not None:
        query += " AND device_id = ?"
        params.append(filters.device_id)
    if filters.action is not None:
        query += " AND action = ?"
        params.append(filters.action.value)
    if filters.operator is not None:
        query += " AND operator = ?"
        params.append(filters.operator)
    if filters.success is not None:
        query += " AND success = ?"
        params.append(1 if filters.success else 0)
    if filters.since is not None:
        query += " AND timestamp >= ?"
        params.append(filters.since.isoformat())
    if filters.until is not None:
        query += " AND timestamp <= ?"
        params.append(filters.until.isoformat())

    query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
    params.append(filters.limit)
    params.append(filters.offset)

    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()

    return [
        HistoryEntry(
            id=row[0],
            device_id=row[1],
            device_name=row[2],
            action=ActionType(row[3]),
            details=row[4],
            operator=row[5],
            success=bool(row[6]),
            timestamp=row[7],
        )
        for row in rows
    ]


async def get_device_history(
    device_id: str, limit: int = 100, offset: int = 0
) -> list[HistoryEntry]:
    """Recupere l'historique d'un appareil specifique.

    Args:
        device_id: Identifiant de l'appareil.
        limit: Nombre maximum d'entrees retournees.
        offset: Decalage pour la pagination.

    Returns:
        Liste d'entrees d'historique pour cet appareil.
    """
    filters = HistoryFilter(device_id=device_id, limit=limit, offset=offset)
    return await get_history(filters)


async def export_history(filters: HistoryFilter) -> list[dict[str, str | bool]]:
    """Exporte l'historique sous forme de liste de dictionnaires.

    Args:
        filters: Criteres de filtrage pour l'export.

    Returns:
        Liste de dictionnaires prets pour serialisation JSON ou CSV.
    """
    entries = await get_history(filters)
    return [
        {
            "id": e.id,
            "device_id": e.device_id,
            "device_name": e.device_name,
            "action": e.action.value,
            "details": e.details,
            "operator": e.operator,
            "success": e.success,
            "timestamp": e.timestamp,
        }
        for e in entries
    ]
