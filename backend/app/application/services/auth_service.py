import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    AccountLockedError,
    ConflictError,
    NotFoundError,
)
from app.config import settings
from app.infrastructure.database.models import UserModel, RefreshTokenModel


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def login(self, email: str, password: str) -> dict:
        stmt = select(UserModel).where(
            UserModel.email == email,
            UserModel.is_active.is_(True),
            UserModel.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise InvalidCredentialsError()

        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise AccountLockedError(user.locked_until.isoformat())

        if not verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.max_login_attempts:
                user.locked_until = datetime.now(timezone.utc) + timedelta(
                    minutes=settings.account_lockout_minutes
                )
            await self.session.flush()
            raise InvalidCredentialsError()

        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.now(timezone.utc)

        access_token = create_access_token(
            {"sub": str(user.id), "role": user.role}
        )
        refresh = create_refresh_token({"sub": str(user.id)})

        refresh_hash = hash_password(refresh)
        rt = RefreshTokenModel(
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(
                days=settings.jwt_refresh_token_expire_days
            ),
        )
        self.session.add(rt)
        await self.session.flush()

        return {
            "access_token": access_token,
            "refresh_token": refresh,
            "token_type": "bearer",
        }

    async def refresh(self, refresh_token: str) -> dict:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid token type")
        except ValueError as e:
            raise AuthenticationError(str(e))

        user_id = uuid.UUID(payload["sub"])
        stmt = select(RefreshTokenModel).where(
            RefreshTokenModel.user_id == user_id,
            RefreshTokenModel.is_revoked.is_(False),
            RefreshTokenModel.expires_at > datetime.now(timezone.utc),
            RefreshTokenModel.is_active.is_(True),
        )
        result = await self.session.execute(stmt)
        stored = None
        for token in result.scalars().all():
            if verify_password(refresh_token, token.token_hash):
                stored = token
                break
        if not stored:
            raise AuthenticationError("Invalid or expired refresh token")

        stored.is_revoked = True

        user_id = uuid.UUID(payload["sub"])
        stmt = select(UserModel).where(
            UserModel.id == user_id,
            UserModel.is_active.is_(True),
        )
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise AuthenticationError("User not found")

        access_token = create_access_token(
            {"sub": str(user.id), "role": user.role}
        )
        new_refresh = create_refresh_token({"sub": str(user.id)})
        new_hash = hash_password(new_refresh)
        rt = RefreshTokenModel(
            user_id=user.id,
            token_hash=new_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(
                days=settings.jwt_refresh_token_expire_days
            ),
        )
        self.session.add(rt)
        await self.session.flush()

        return {
            "access_token": access_token,
            "refresh_token": new_refresh,
            "token_type": "bearer",
        }

    async def get_current_user(self, user_id: str) -> UserModel:
        try:
            uid = uuid.UUID(user_id)
        except ValueError:
            raise AuthenticationError("Invalid user ID format")
        stmt = select(UserModel).where(
            UserModel.id == uid,
            UserModel.is_active.is_(True),
            UserModel.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User", user_id)
        return user

    async def register(
        self, email: str, password: str, full_name: str, role: str = "viewer"
    ) -> UserModel:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        if result.scalar_one_or_none():
            raise ConflictError("Email already registered")

        user = UserModel(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def change_password(
        self, user_id: str, current_password: str, new_password: str
    ) -> None:
        user = await self.get_current_user(user_id)
        if not verify_password(current_password, user.password_hash):
            raise InvalidCredentialsError()
        user.password_hash = hash_password(new_password)
        await self.session.flush()
