import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, require_role
from app.application.services.department_service import LaboratoryService
from app.application.dto.responses import ResponseBase
from pydantic import BaseModel, Field


class LabCreateRequest(BaseModel):
    college_id: str
    department_id: str
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    capacity: int
    building: str = Field(..., max_length=255)
    floor: int = 0
    equipment: dict = Field(default_factory=dict)


class LabResponse(ResponseBase):
    id: str
    college_id: str
    department_id: str
    name: str
    code: str
    capacity: int
    building: str
    floor: int
    equipment: dict
    is_active: bool


router = APIRouter(prefix="/laboratories", tags=["Laboratories"])


@router.get("")
async def list_laboratories(
    college_id: uuid.UUID | None = Query(None),
    department_id: uuid.UUID | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = LaboratoryService(session)
    filters = {}
    if college_id:
        filters["college_id"] = college_id
    if department_id:
        filters["department_id"] = department_id
    items, total = await service.list(offset=offset, limit=limit, **filters)
    return {"items": [LabResponse.model_validate(l) for l in items], "total": total, "offset": offset, "limit": limit}


@router.post("", status_code=201)
async def create_laboratory(
    request: LabCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = LaboratoryService(session)
    lab = await service.create(**request.model_dump())
    return LabResponse.model_validate(lab)


@router.get("/{lab_id}")
async def get_laboratory(
    lab_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = LaboratoryService(session)
    lab = await service.get_by_id(lab_id)
    return LabResponse.model_validate(lab)


@router.put("/{lab_id}")
async def update_laboratory(
    lab_id: uuid.UUID,
    request: LabCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = LaboratoryService(session)
    updates = request.model_dump(exclude_unset=True)
    lab = await service.update(lab_id, **updates)
    return LabResponse.model_validate(lab)


@router.delete("/{lab_id}")
async def delete_laboratory(
    lab_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = LaboratoryService(session)
    await service.delete(lab_id)
    return {"success": True}
