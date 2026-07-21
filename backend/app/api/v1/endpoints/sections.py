import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, require_role
from app.application.services.department_service import SectionService
from app.application.dto.responses import ResponseBase
from pydantic import BaseModel, Field


class SectionCreateRequest(BaseModel):
    semester_id: str
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    strength: int = 0


class SectionUpdateRequest(BaseModel):
    name: str | None = Field(None, max_length=255)
    code: str | None = Field(None, max_length=50)
    strength: int | None = None


class SectionResponse(ResponseBase):
    id: str
    semester_id: str
    name: str
    code: str
    strength: int
    is_active: bool


router = APIRouter(prefix="/sections", tags=["Sections"])


@router.get("")
async def list_sections(
    semester_id: uuid.UUID | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = SectionService(session)
    filters = {}
    if semester_id:
        filters["semester_id"] = semester_id
    items, total = await service.list(offset=offset, limit=limit, **filters)
    return {"items": [SectionResponse.model_validate(s) for s in items], "total": total, "offset": offset, "limit": limit}


@router.post("", status_code=201)
async def create_section(
    request: SectionCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("coordinator")),
):
    service = SectionService(session)
    sec = await service.create(**request.model_dump())
    return SectionResponse.model_validate(sec)


@router.get("/{section_id}")
async def get_section(
    section_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = SectionService(session)
    sec = await service.get_by_id(section_id)
    return SectionResponse.model_validate(sec)


@router.put("/{section_id}")
async def update_section(
    section_id: uuid.UUID,
    request: SectionUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("coordinator")),
):
    service = SectionService(session)
    updates = request.model_dump(exclude_unset=True)
    sec = await service.update(section_id, **updates)
    return SectionResponse.model_validate(sec)


@router.delete("/{section_id}")
async def delete_section(
    section_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = SectionService(session)
    await service.delete(section_id)
    return {"success": True}
