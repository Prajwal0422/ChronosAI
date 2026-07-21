import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, require_role
from app.application.dto.auth import UserResponse
from app.application.services.auth_service import AuthService
from pydantic import BaseModel, Field


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(None, max_length=255)
    college_id: str | None = None
    department_id: str | None = None


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
async def list_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    from app.infrastructure.database.repositories.base import BaseRepository
    from app.infrastructure.database.models import UserModel
    repo = BaseRepository(UserModel, session)
    items, total = await repo.list(offset=offset, limit=limit)
    return {"items": [UserResponse.model_validate(u) for u in items], "total": total, "offset": offset, "limit": limit}


@router.get("/{user_id}")
async def get_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    auth_service = AuthService(session)
    user = await auth_service.get_current_user(str(user_id))
    return UserResponse.model_validate(user)


@router.put("/{user_id}")
async def update_user(
    user_id: uuid.UUID,
    request: UserUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    from app.infrastructure.database.repositories.base import BaseRepository
    from app.infrastructure.database.models import UserModel
    repo = BaseRepository(UserModel, session)
    updates = request.model_dump(exclude_unset=True)
    user = await repo.update(user_id, **updates)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    from app.infrastructure.database.repositories.base import BaseRepository
    from app.infrastructure.database.models import UserModel
    repo = BaseRepository(UserModel, session)
    await repo.soft_delete(user_id)
    return {"success": True}
