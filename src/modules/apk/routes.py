"""Routes FastAPI pour la gestion des APKs."""

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse

from src.models import APKInfo
from src.modules.apk.service import (
    delete_apk,
    get_apk_info,
    get_apk_path,
    list_apks,
    save_apk,
)

router = APIRouter(prefix="/api/apk", tags=["apk"])


@router.get("/", response_model=list[APKInfo])
async def route_list_apks() -> list[APKInfo]:
    """Liste tous les APKs disponibles.

    Returns:
        Liste des APKInfo avec metadonnees.
    """
    return await list_apks()


@router.post("/upload", response_model=APKInfo)
async def route_upload_apk(
    file: UploadFile,
    version: str = "0.0.1",
    description: str = "",
) -> APKInfo:
    """Upload un fichier APK.

    Args:
        file: Fichier APK a uploader.
        version: Version de l'APK.
        description: Description de l'APK.

    Returns:
        APKInfo de l'APK sauvegarde.

    Raises:
        HTTPException: Si le fichier n'est pas un APK.
    """
    filename = file.filename or "unknown.apk"
    if not filename.endswith(".apk"):
        raise HTTPException(status_code=400, detail="Le fichier doit etre un .apk")
    content = await file.read()
    return await save_apk(
        filename=filename,
        content=content,
        version=version,
        description=description,
    )


@router.get("/{name}/download")
async def route_download_apk(name: str) -> FileResponse:
    """Telecharge un fichier APK.

    Args:
        name: Nom de l'APK (sans extension).

    Returns:
        FileResponse avec le fichier APK.

    Raises:
        HTTPException: Si l'APK n'existe pas.
    """
    path = await get_apk_path(name)
    if path is None:
        raise HTTPException(status_code=404, detail=f"APK '{name}' non trouve")
    return FileResponse(
        path=str(path),
        filename=path.name,
        media_type="application/vnd.android.package-archive",
    )


@router.get("/{name}/info", response_model=APKInfo)
async def route_get_apk_info(name: str) -> APKInfo:
    """Recupere les informations d'un APK.

    Args:
        name: Nom de l'APK (sans extension).

    Returns:
        APKInfo avec metadonnees.

    Raises:
        HTTPException: Si l'APK n'existe pas.
    """
    info = await get_apk_info(name)
    if info is None:
        raise HTTPException(status_code=404, detail=f"APK '{name}' non trouve")
    return info


@router.delete("/{name}")
async def route_delete_apk(name: str) -> dict[str, str]:
    """Supprime un APK et ses metadonnees.

    Args:
        name: Nom de l'APK (sans extension).

    Returns:
        Message de confirmation.

    Raises:
        HTTPException: Si l'APK n'existe pas.
    """
    deleted = await delete_apk(name)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"APK '{name}' non trouve")
    return {"message": f"APK '{name}' supprime"}
