import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, require_role
from app.application.services.department_service import TimeSlotService
from app.application.dto.responses import ResponseBase
from pydantic import BaseModel, Field


class TimeSlotCreateRequest(BaseModel):
    college_id: str
    name: str = Field(..., min_length=1, max_length=255)
    day_of_week: str
    start_time: str
    end_time: str
    slot_type: str = "lecture"
    slot_group: str | None = None


class TimeSlotResponse(ResponseBase):
    id: str
    college_id: str
    name: str
    day_of_week: str
    start_time: str
    end_time: str
    slot_type: str
    slot_group: str | None
    is_active: bool


router = APIRouter(prefix="/time-slots", tags=["Time Slots"])


@router.get("")
async def list_time_slots(
    college_id: uuid.UUID | None = Query(None),
    day_of_week: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = TimeSlotService(session)
    filters = {}
    if college_id:
        filters["college_id"] = college_id
    if day_of_week:
        filters["day_of_week"] = day_of_week
    items, total = await service.list(offset=offset, limit=limit, **filters)
    return {"items": [TimeSlotResponse.model_validate(t) for t in items], "total": total, "offset": offset, "limit": limit}


@router.post("", status_code=201)
async def create_time_slot(
    request: TimeSlotCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = TimeSlotService(session)
    ts = await service.create(**request.model_dump())
    return TimeSlotResponse.model_validate(ts)


@router.get("/{slot_id}")
async def get_time_slot(
    slot_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = TimeSlotService(session)
    ts = await service.get_by_id(slot_id)
    return TimeSlotResponse.model_validate(ts)


@router.put("/{slot_id}")
async def update_time_slot(
    slot_id: uuid.UUID,
    request: TimeSlotCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = TimeSlotService(session)
    updates = request.model_dump(exclude_unset=True)
    ts = await service.update(slot_id, **updates)
    return TimeSlotResponse.model_validate(ts)


@router.delete("/{slot_id}")
async def delete_time_slot(
    slot_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = TimeSlotService(session)
    await service.delete(slot_id)
    return {"success": True}
