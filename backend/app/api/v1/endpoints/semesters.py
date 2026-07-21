import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, require_role
from app.application.dto.common import SuccessResponse
from app.application.services.department_service import SemesterService
from app.application.dto.responses import ResponseBase
from pydantic import BaseModel, Field


class SemesterCreateRequest(BaseModel):
    department_id: str
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    year: int
    order: int


class SemesterUpdateRequest(BaseModel):
    name: str | None = Field(None, max_length=255)
    code: str | None = Field(None, max_length=50)
    year: int | None = None
    order: int | None = None


class SemesterResponse(ResponseBase):
    id: str
    department_id: str
    name: str
    code: str
    year: int
    order: int
    is_active: bool


router = APIRouter(prefix="/semesters", tags=["Semesters"])


@router.get("")
async def list_semesters(
    department_id: uuid.UUID | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = SemesterService(session)
    filters = {}
    if department_id:
        filters["department_id"] = department_id
    items, total = await service.list(offset=offset, limit=limit, **filters)
    return {"items": [SemesterResponse.model_validate(s) for s in items], "total": total, "offset": offset, "limit": limit}


@router.post("", status_code=201)
async def create_semester(
    request: SemesterCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = SemesterService(session)
    sem = await service.create(**request.model_dump())
    return SemesterResponse.model_validate(sem)


@router.get("/{semester_id}")
async def get_semester(
    semester_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = SemesterService(session)
    sem = await service.get_by_id(semester_id)
    return SemesterResponse.model_validate(sem)


@router.put("/{semester_id}")
async def update_semester(
    semester_id: uuid.UUID,
    request: SemesterUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = SemesterService(session)
    updates = request.model_dump(exclude_unset=True)
    sem = await service.update(semester_id, **updates)
    return SemesterResponse.model_validate(sem)


@router.delete("/{semester_id}")
async def delete_semester(
    semester_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = SemesterService(session)
    await service.delete(semester_id)
    return SuccessResponse()
