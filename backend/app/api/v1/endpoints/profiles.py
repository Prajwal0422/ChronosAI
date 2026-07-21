from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, get_current_user_id
from app.application.dto.auth import UserResponse, ChangePasswordRequest
from app.application.services.auth_service import AuthService
from pydantic import BaseModel, Field


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(None, max_length=255)


router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("")
async def get_profile(
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    auth_service = AuthService(session)
    user = await auth_service.get_current_user(user_id)
    return UserResponse.model_validate(user)


@router.put("")
async def update_profile(
    request: ProfileUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    from app.infrastructure.database.repositories.base import BaseRepository
    from app.infrastructure.database.models import UserModel
    repo = BaseRepository(UserModel, session)
    updates = request.model_dump(exclude_unset=True)
    user = await repo.update(user_id, **updates)
    return UserResponse.model_validate(user)


@router.put("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    auth_service = AuthService(session)
    await auth_service.change_password(
        user_id, request.current_password, request.new_password
    )
    return {"success": True, "message": "Password changed successfully"}
