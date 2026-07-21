import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, require_role
from app.application.dto.constraint import (
    ConstraintCreateRequest,
    ConstraintUpdateRequest,
    ConstraintResponse,
)
from app.application.services.constraint_service import ConstraintService

router = APIRouter(prefix="/constraints", tags=["Constraints"])


@router.get("")
async def list_constraints(
    college_id: uuid.UUID | None = Query(None),
    department_id: uuid.UUID | None = Query(None),
    constraint_type: str | None = Query(None),
    category: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = ConstraintService(session)
    filters = {}
    if college_id:
        filters["college_id"] = college_id
    if department_id:
        filters["department_id"] = department_id
    if constraint_type:
        filters["constraint_type"] = constraint_type
    if category:
        filters["category"] = category
    items, total = await service.list(offset=offset, limit=limit, **filters)
    return {"items": [ConstraintResponse.model_validate(c) for c in items], "total": total, "offset": offset, "limit": limit}


@router.post("", status_code=201)
async def create_constraint(
    request: ConstraintCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("coordinator")),
):
    service = ConstraintService(session)
    c = await service.create(**request.model_dump())
    return ConstraintResponse.model_validate(c)


@router.post("/validate")
async def validate_constraint(
    request: ConstraintCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("coordinator")),
):
    service = ConstraintService(session)
    await service.validate_constraint_config(
        request.constraint_type, request.category, request.config
    )
    return {"success": True, "message": "Constraint configuration is valid"}


@router.get("/{constraint_id}")
async def get_constraint(
    constraint_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = ConstraintService(session)
    c = await service.get_by_id(constraint_id)
    return ConstraintResponse.model_validate(c)


@router.put("/{constraint_id}")
async def update_constraint(
    constraint_id: uuid.UUID,
    request: ConstraintUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("coordinator")),
):
    service = ConstraintService(session)
    updates = request.model_dump(exclude_unset=True)
    c = await service.update(constraint_id, **updates)
    return ConstraintResponse.model_validate(c)


@router.delete("/{constraint_id}")
async def delete_constraint(
    constraint_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = ConstraintService(session)
    await service.delete(constraint_id)
    return {"success": True}
