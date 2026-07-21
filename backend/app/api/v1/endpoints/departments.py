import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, require_role
from app.application.dto.department import DepartmentCreateRequest, DepartmentUpdateRequest, DepartmentResponse
from app.application.services.department_service import DepartmentService

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("")
async def list_departments(
    college_id: uuid.UUID | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = DepartmentService(session)
    filters = {}
    if college_id:
        filters["college_id"] = college_id
    items, total = await service.list(offset=offset, limit=limit, **filters)
    return {"items": [DepartmentResponse.model_validate(d) for d in items], "total": total, "offset": offset, "limit": limit}


@router.post("", status_code=201)
async def create_department(
    request: DepartmentCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = DepartmentService(session)
    dept = await service.create(**request.model_dump())
    return DepartmentResponse.model_validate(dept)


@router.get("/{department_id}")
async def get_department(
    department_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = DepartmentService(session)
    dept = await service.get_by_id(department_id)
    return DepartmentResponse.model_validate(dept)


@router.put("/{department_id}")
async def update_department(
    department_id: uuid.UUID,
    request: DepartmentUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = DepartmentService(session)
    updates = request.model_dump(exclude_unset=True)
    dept = await service.update(department_id, **updates)
    return DepartmentResponse.model_validate(dept)


@router.delete("/{department_id}")
async def delete_department(
    department_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = DepartmentService(session)
    await service.delete(department_id)
    return {"success": True}
