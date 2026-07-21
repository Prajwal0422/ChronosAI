import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, get_current_user_id, require_role
from app.application.dto.college import CollegeCreateRequest, CollegeUpdateRequest, CollegeResponse
from app.application.services.college_service import CollegeService

router = APIRouter(prefix="/colleges", tags=["Colleges"])


@router.get("")
async def list_colleges(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = CollegeService(session)
    items, total = await service.list(offset=offset, limit=limit)
    return {"items": [CollegeResponse.model_validate(c) for c in items], "total": total, "offset": offset, "limit": limit}


@router.post("", status_code=201)
async def create_college(
    request: CollegeCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = CollegeService(session)
    college = await service.create_college(
        name=request.name,
        code=request.code,
        college_type=request.college_type,
        academic_year=request.academic_year,
        address=request.address,
        phone=request.phone,
        email=request.email,
        website=request.website,
    )
    return CollegeResponse.model_validate(college)


@router.get("/{college_id}")
async def get_college(
    college_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = CollegeService(session)
    college = await service.get_by_id(college_id)
    return CollegeResponse.model_validate(college)


@router.put("/{college_id}")
async def update_college(
    college_id: uuid.UUID,
    request: CollegeUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = CollegeService(session)
    updates = request.model_dump(exclude_unset=True)
    college = await service.update(college_id, **updates)
    return CollegeResponse.model_validate(college)


@router.delete("/{college_id}")
async def delete_college(
    college_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = CollegeService(session)
    await service.delete(college_id)
    return {"success": True, "message": "College deleted successfully"}
