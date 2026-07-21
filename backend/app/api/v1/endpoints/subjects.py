import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, require_role
from app.application.services.department_service import SubjectService
from app.application.dto.responses import ResponseBase
from pydantic import BaseModel, Field


class SubjectCreateRequest(BaseModel):
    department_id: str
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    subject_type: str = "theory"
    lectures_per_week: int = 1
    is_elective: bool = False
    is_lab: bool = False
    lab_duration: int | None = None


class SubjectUpdateRequest(BaseModel):
    name: str | None = Field(None, max_length=255)
    subject_type: str | None = None
    lectures_per_week: int | None = None
    is_elective: bool | None = None
    is_lab: bool | None = None
    lab_duration: int | None = None


class SubjectResponse(ResponseBase):
    id: str
    department_id: str
    name: str
    code: str
    subject_type: str
    lectures_per_week: int
    is_elective: bool
    is_lab: bool
    lab_duration: int | None
    is_active: bool


router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("")
async def list_subjects(
    department_id: uuid.UUID | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = SubjectService(session)
    filters = {}
    if department_id:
        filters["department_id"] = department_id
    items, total = await service.list(offset=offset, limit=limit, **filters)
    return {"items": [SubjectResponse.model_validate(s) for s in items], "total": total, "offset": offset, "limit": limit}


@router.post("", status_code=201)
async def create_subject(
    request: SubjectCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("coordinator")),
):
    service = SubjectService(session)
    subject = await service.create(**request.model_dump())
    return SubjectResponse.model_validate(subject)


@router.get("/{subject_id}")
async def get_subject(
    subject_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = SubjectService(session)
    subject = await service.get_by_id(subject_id)
    return SubjectResponse.model_validate(subject)


@router.put("/{subject_id}")
async def update_subject(
    subject_id: uuid.UUID,
    request: SubjectUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("coordinator")),
):
    service = SubjectService(session)
    updates = request.model_dump(exclude_unset=True)
    subject = await service.update(subject_id, **updates)
    return SubjectResponse.model_validate(subject)


@router.delete("/{subject_id}")
async def delete_subject(
    subject_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = SubjectService(session)
    await service.delete(subject_id)
    return {"success": True}
