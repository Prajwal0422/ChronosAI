import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, get_current_user_id, require_role
from app.application.services.timetable_service import ConflictService
from app.application.dto.responses import ResponseBase
from pydantic import BaseModel


class ConflictResponse(ResponseBase):
    id: str
    timetable_id: str
    conflict_type: str
    severity: str
    description: str
    involved_entries: list
    resolved: bool
    resolution: str | None
    resolved_by: str | None
    resolved_at: str | None


class ResolveRequest(BaseModel):
    resolution: str


router = APIRouter(prefix="/conflicts", tags=["Conflicts"])


@router.get("")
async def list_conflicts(
    timetable_id: uuid.UUID | None = Query(None),
    resolved: bool | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = ConflictService(session)
    if timetable_id:
        items = await service.get_timetable_conflicts(timetable_id, resolved)
        return {"items": [ConflictResponse.model_validate(c) for c in items], "total": len(items), "offset": 0, "limit": len(items)}
    items, total = await service.list(offset=offset, limit=limit)
    return {"items": [ConflictResponse.model_validate(c) for c in items], "total": total, "offset": offset, "limit": limit}


@router.get("/{conflict_id}")
async def get_conflict(
    conflict_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = ConflictService(session)
    c = await service.get_by_id(conflict_id)
    return ConflictResponse.model_validate(c)


@router.post("/{conflict_id}/resolve")
async def resolve_conflict(
    conflict_id: uuid.UUID,
    request: ResolveRequest,
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
    _: str = Depends(require_role("coordinator")),
):
    service = ConflictService(session)
    c = await service.resolve_conflict(
        conflict_id, request.resolution, uuid.UUID(user_id)
    )
    return ConflictResponse.model_validate(c)


@router.post("/auto-resolve")
async def auto_resolve_conflicts(
    timetable_id: uuid.UUID = Query(...),
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
    _: str = Depends(require_role("coordinator")),
):
    service = ConflictService(session)
    conflicts = await service.get_timetable_conflicts(timetable_id, resolved=False)
    resolved_count = 0
    for c in conflicts:
        await service.resolve_conflict(
            c.id, "Auto-resolved by system", uuid.UUID(user_id)
        )
        resolved_count += 1
    return {"success": True, "resolved_count": resolved_count}
