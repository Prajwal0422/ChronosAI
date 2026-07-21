import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, require_role
from app.application.services.department_service import ClassroomService
from app.application.dto.responses import ResponseBase
from pydantic import BaseModel, Field


class ClassroomCreateRequest(BaseModel):
    college_id: str
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    capacity: int
    building: str = Field(..., max_length=255)
    floor: int = 0
    room_type: str = "lecture"
    facilities: dict = Field(default_factory=dict)


class ClassroomResponse(ResponseBase):
    id: str
    college_id: str
    name: str
    code: str
    capacity: int
    building: str
    floor: int
    room_type: str
    facilities: dict
    is_active: bool


router = APIRouter(prefix="/classrooms", tags=["Classrooms"])


@router.get("")
async def list_classrooms(
    college_id: uuid.UUID | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = ClassroomService(session)
    filters = {}
    if college_id:
        filters["college_id"] = college_id
    items, total = await service.list(offset=offset, limit=limit, **filters)
    return {"items": [ClassroomResponse.model_validate(c) for c in items], "total": total, "offset": offset, "limit": limit}


@router.post("", status_code=201)
async def create_classroom(
    request: ClassroomCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = ClassroomService(session)
    cr = await service.create(**request.model_dump())
    return ClassroomResponse.model_validate(cr)


@router.get("/{classroom_id}")
async def get_classroom(
    classroom_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = ClassroomService(session)
    cr = await service.get_by_id(classroom_id)
    return ClassroomResponse.model_validate(cr)


@router.put("/{classroom_id}")
async def update_classroom(
    classroom_id: uuid.UUID,
    request: ClassroomCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = ClassroomService(session)
    updates = request.model_dump(exclude_unset=True)
    cr = await service.update(classroom_id, **updates)
    return ClassroomResponse.model_validate(cr)


@router.delete("/{classroom_id}")
async def delete_classroom(
    classroom_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = ClassroomService(session)
    await service.delete(classroom_id)
    return {"success": True}
