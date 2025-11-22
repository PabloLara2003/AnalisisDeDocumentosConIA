import os
from fastapi import UploadFile, HTTPException, status
from ..config import settings


def _get_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


async def validate_uploaded_file(file: UploadFile) -> bytes:
    """
    Valida tipo, extensión y tamaño del archivo.
    Devuelve el contenido en bytes si todo es correcto.
    Lanza HTTPException si hay algo sospechoso.
    """
    ext = _get_extension(file.filename or "")
    if ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extensión no permitida: {ext}",
        )

    if file.content_type not in settings.allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de contenido no permitido: {file.content_type}",
        )

    max_bytes = settings.max_file_size_mb * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"Archivo demasiado grande. Máximo permitido: "
                f"{settings.max_file_size_mb} MB"
            ),
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Archivo vacío",
        )

    return content
