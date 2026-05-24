"""Routes FastAPI pour le module d'historique."""

import csv
import io
from datetime import datetime

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from src.models import ActionType, HistoryCreate, HistoryEntry, HistoryFilter
from src.modules.history.service import (
    export_history,
    get_device_history,
    get_history,
    log_action,
)

router = APIRouter(prefix="/api/history", tags=["history"])

CSV_COLUMNS = [
    "id",
    "device_id",
    "device_name",
    "action",
    "details",
    "operator",
    "success",
    "timestamp",
]


@router.get("/", response_model=list[HistoryEntry])
async def list_history(
    device_id: str | None = Query(None, description="Filtrer par appareil"),
    action: ActionType | None = Query(None, description="Filtrer par type d'action"),
    operator: str | None = Query(None, description="Filtrer par operateur"),
    success: bool | None = Query(None, description="Filtrer par succes/echec"),
    since: datetime | None = Query(None, description="Date de debut (ISO 8601)"),
    until: datetime | None = Query(None, description="Date de fin (ISO 8601)"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre max de resultats"),
    offset: int = Query(0, ge=0, description="Decalage pour pagination"),
) -> list[HistoryEntry]:
    """Liste l'historique avec filtres optionnels.

    Returns:
        Liste d'entrees d'historique correspondant aux filtres.
    """
    filters = HistoryFilter(
        device_id=device_id,
        action=action,
        operator=operator,
        success=success,
        since=since,
        until=until,
        limit=limit,
        offset=offset,
    )
    return await get_history(filters)


@router.get("/export")
async def export_history_endpoint(
    format: str = Query("json", description="Format d'export: json ou csv"),
    device_id: str | None = Query(None, description="Filtrer par appareil"),
    action: ActionType | None = Query(None, description="Filtrer par type d'action"),
    operator: str | None = Query(None, description="Filtrer par operateur"),
    success: bool | None = Query(None, description="Filtrer par succes/echec"),
    since: datetime | None = Query(None, description="Date de debut (ISO 8601)"),
    until: datetime | None = Query(None, description="Date de fin (ISO 8601)"),
    limit: int = Query(1000, ge=1, le=10000, description="Nombre max de resultats"),
    offset: int = Query(0, ge=0, description="Decalage pour pagination"),
) -> list[dict[str, str | bool]] | StreamingResponse:
    """Exporte l'historique en JSON ou CSV.

    Args:
        format: Format de sortie (json ou csv).

    Returns:
        Donnees JSON ou flux CSV selon le format demande.
    """
    filters = HistoryFilter(
        device_id=device_id,
        action=action,
        operator=operator,
        success=success,
        since=since,
        until=until,
        limit=limit,
        offset=offset,
    )
    data = await export_history(filters)

    if format == "csv":
        return _build_csv_response(data)

    return data


def _build_csv_response(data: list[dict[str, str | bool]]) -> StreamingResponse:
    """Construit une reponse CSV a partir des donnees.

    Args:
        data: Liste de dictionnaires a convertir en CSV.

    Returns:
        StreamingResponse avec le contenu CSV.
    """
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS)
    writer.writeheader()
    writer.writerows(data)
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=history_export.csv"},
    )


@router.get("/{device_id}", response_model=list[HistoryEntry])
async def device_history(
    device_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Nombre max de resultats"),
    offset: int = Query(0, ge=0, description="Decalage pour pagination"),
) -> list[HistoryEntry]:
    """Recupere l'historique d'un appareil specifique.

    Args:
        device_id: Identifiant de l'appareil.
        limit: Nombre maximum d'entrees retournees.
        offset: Decalage pour la pagination.

    Returns:
        Liste d'entrees d'historique pour cet appareil.
    """
    return await get_device_history(device_id, limit=limit, offset=offset)


@router.post("/", response_model=HistoryEntry, status_code=201)
async def create_history_entry(entry: HistoryCreate) -> HistoryEntry:
    """Enregistre une nouvelle action dans l'historique.

    Args:
        entry: Donnees de l'action a enregistrer.

    Returns:
        Entree d'historique creee avec id et timestamp.
    """
    return await log_action(entry)
