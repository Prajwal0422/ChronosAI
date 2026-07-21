import uuid
import secrets
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from app.api.v1.deps import get_db_session, get_current_user_id
from app.application.dto.auth import (
    LoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
)
from app.application.services.auth_service import AuthService
from app.application.services.college_service import CollegeService
from app.core.exceptions import AuthenticationError, ConflictError, AppException
from app.infrastructure.database.models import UserModel, SystemSettingsModel
from app.core.security import hash_password
from app.core.constants import UserRole, CollegeType

router = APIRouter(prefix="/auth", tags=["Authentication"])


class UpdateMeRequest(BaseModel):
    college_id: str | None = None
    department_id: str | None = None
    full_name: str | None = Field(None, max_length=255)


class SetupResponse(BaseModel):
    message: str
    admin_email: str
    admin_password: str
    college_name: str


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
):
    service = AuthService(session)
    result = await service.login(request.email, request.password)
    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db_session),
):
    service = AuthService(session)
    result = await service.refresh(request.refresh_token)
    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
):
    from app.infrastructure.database.models import UserModel
    from sqlalchemy import select

    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise AuthenticationError("Invalid user ID format")
    stmt = select(UserModel).where(UserModel.id == uid)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise AuthenticationError("User not found")
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        college_id=str(user.college_id) if user.college_id else None,
        department_id=str(user.department_id) if user.department_id else None,
        is_active=user.is_active,
    )


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    request: UpdateMeRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
):
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise AuthenticationError("Invalid user ID format")

    stmt = select(UserModel).where(UserModel.id == uid)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise AuthenticationError("User not found")

    updates = request.model_dump(exclude_unset=True)
    if "college_id" in updates and updates["college_id"] is not None:
        updates["college_id"] = uuid.UUID(updates["college_id"])
    if "department_id" in updates and updates["department_id"] is not None:
        updates["department_id"] = uuid.UUID(updates["department_id"])

    for key, value in updates.items():
        setattr(user, key, value)
    await session.flush()

    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        college_id=str(user.college_id) if user.college_id else None,
        department_id=str(user.department_id) if user.department_id else None,
        is_active=user.is_active,
    )


@router.post("/setup", response_model=SetupResponse)
async def setup_system(
    session: AsyncSession = Depends(get_db_session),
):
    stmt = select(UserModel).where(UserModel.role == UserRole.ADMIN, UserModel.is_active.is_(True))
    result = await session.execute(stmt)
    existing_admin = result.scalar_one_or_none()

    if existing_admin:
        return SetupResponse(
            message="System already initialized",
            admin_email=existing_admin.email,
            admin_password="(hidden)",
            college_name="(already configured)",
        )

    init_setting = await session.execute(
        select(SystemSettingsModel).where(SystemSettingsModel.key == "system_initialized")
    )
    if init_setting.scalar_one_or_none():
        raise AppException("SETUP_ALREADY_DONE", "System setup was already completed", status_code=400)

    admin_password = secrets.token_urlsafe(12)
    admin_email = "admin@chronosai.edu"

    admin = UserModel(
        email=admin_email,
        password_hash=hash_password(admin_password),
        full_name="System Administrator",
        role=UserRole.ADMIN,
        is_superuser=True,
    )
    session.add(admin)
    await session.flush()

    college_service = CollegeService(session)
    college = await college_service.create_college(
        name="ABC Engineering College",
        code="ABCEC",
        college_type=CollegeType.DEGREE,
        academic_year="2025-2026",
        address="123 Education Street, Tech City",
        phone="+1-555-0100",
        email="info@abcec.edu",
        website="https://abcec.edu",
    )

    admin.college_id = college.id
    session.add(SystemSettingsModel(key="system_initialized", value="true"))
    await session.flush()

    return SetupResponse(
        message="System initialized successfully",
        admin_email=admin_email,
        admin_password=admin_password,
        college_name=college.name,
    )


@router.post("/register", response_model=UserResponse)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
):
    from app.core.security import hash_password
    from app.infrastructure.database.models import UserModel
    stmt = select(UserModel).where(UserModel.email == request.email)
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise ConflictError("Email already registered")

    user = UserModel(
        email=request.email,
        password_hash=hash_password(request.password),
        full_name=request.full_name,
        role="viewer",
    )
    session.add(user)
    await session.flush()
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
    )
