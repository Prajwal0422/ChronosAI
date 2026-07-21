import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, require_role
from app.application.services.department_service import TeacherService
from app.application.dto.responses import ResponseBase
from pydantic import BaseModel, Field


class TeacherCreateRequest(BaseModel):
    department_id: str
    employee_code: str = Field(..., min_length=1, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., max_length=255)
    phone: str | None = Field(None, max_length=50)
    qualification: str | None = Field(None, max_length=255)
    specialization: str | None = Field(None, max_length=255)
    max_lectures_per_day: int = 6
    max_lectures_per_week: int = 30
    max_consecutive_lectures: int = 3
    is_shared: bool = False


class TeacherUpdateRequest(BaseModel):
    full_name: str | None = Field(None, max_length=255)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    qualification: str | None = Field(None, max_length=255)
    specialization: str | None = Field(None, max_length=255)
    max_lectures_per_day: int | None = None
    max_lectures_per_week: int | None = None
    max_consecutive_lectures: int | None = None
    is_shared: bool | None = None


class TeacherResponse(ResponseBase):
    id: str
    department_id: str
    employee_code: str
    full_name: str
    email: str
    phone: str | None
    qualification: str | None
    specialization: str | None
    max_lectures_per_day: int
    max_lectures_per_week: int
    max_consecutive_lectures: int
    is_shared: bool
    is_active: bool


router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.get("")
async def list_teachers(
    department_id: uuid.UUID | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = TeacherService(session)
    filters = {}
    if department_id:
        filters["department_id"] = department_id
    items, total = await service.list(offset=offset, limit=limit, **filters)
    return {"items": [TeacherResponse.model_validate(t) for t in items], "total": total, "offset": offset, "limit": limit}


@router.post("", status_code=201)
async def create_teacher(
    request: TeacherCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = TeacherService(session)
    teacher = await service.create(**request.model_dump())
    return TeacherResponse.model_validate(teacher)


@router.get("/{teacher_id}")
async def get_teacher(
    teacher_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = TeacherService(session)
    teacher = await service.get_by_id(teacher_id)
    return TeacherResponse.model_validate(teacher)


@router.put("/{teacher_id}")
async def update_teacher(
    teacher_id: uuid.UUID,
    request: TeacherUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = TeacherService(session)
    updates = request.model_dump(exclude_unset=True)
    teacher = await service.update(teacher_id, **updates)
    return TeacherResponse.model_validate(teacher)


@router.delete("/{teacher_id}")
async def delete_teacher(
    teacher_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = TeacherService(session)
    await service.delete(teacher_id)
    return {"success": True}
