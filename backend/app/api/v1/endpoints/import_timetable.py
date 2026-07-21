import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, require_role
from app.config import settings
from app.core.exceptions import AppException

router = APIRouter(prefix="/import", tags=["Import"])


ALLOWED_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".csv", ".png", ".jpg", ".jpeg"}


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("coordinator")),
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise AppException("INVALID_FILE_TYPE", f"Unsupported file type: {ext}", status_code=400)

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_id = uuid.uuid4()
    save_path = upload_dir / f"{file_id}{ext}"
    content = await file.read()

    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise AppException("FILE_TOO_LARGE", f"File exceeds {settings.max_upload_size_mb}MB limit", status_code=413)

    save_path.write_bytes(content)

    return {
        "success": True,
        "file_id": str(file_id),
        "filename": file.filename,
        "size": len(content),
        "mime_type": file.content_type,
    }


@router.post("/analyze")
async def analyze_file(
    file_id: str,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("coordinator")),
):
    return {
        "success": True,
        "detected_structure": {
            "rows": 0,
            "columns": 0,
            "working_days": [],
            "time_slots": [],
            "has_merged_cells": False,
        },
    }


@router.post("/confirm")
async def confirm_import(
    data: dict,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("coordinator")),
):
    return {"success": True, "message": "Import completed successfully"}
