from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, require_role
from app.infrastructure.database.repositories.base import BaseRepository
from app.infrastructure.database.models import SystemSettingsModel

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("")
async def list_settings(
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    repo = BaseRepository(SystemSettingsModel, session)
    items, total = await repo.list()
    return {
        "items": [{"key": s.key, "value": s.value, "description": s.description} for s in items],
        "total": total,
    }


@router.get("/{key}")
async def get_setting(
    key: str,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    repo = BaseRepository(SystemSettingsModel, session)
    items, _ = await repo.list(key=key)
    if not items:
        return {"key": key, "value": None}
    return {"key": items[0].key, "value": items[0].value}


@router.put("/{key}")
async def update_setting(
    key: str,
    value: str,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    repo = BaseRepository(SystemSettingsModel, session)
    items, _ = await repo.list(key=key)
    if items:
        await repo.update(items[0].id, value=value)
    else:
        await repo.create(key=key, value=value)
    return {"success": True, "key": key, "value": value}
