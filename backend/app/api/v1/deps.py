import uuid
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_token
from app.infrastructure.database.session import get_db


async def get_current_user_id(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationError("Missing or invalid authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token payload")
        return user_id
    except ValueError as e:
        raise AuthenticationError(str(e))


async def get_current_user_role(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationError("Missing or invalid authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
        role = payload.get("role", "viewer")
        return role
    except ValueError as e:
        raise AuthenticationError(str(e))


def require_role(required_role: str):
    async def role_checker(role: str = Depends(get_current_user_role)) -> str:
        role_hierarchy = {
            "viewer": 0,
            "faculty": 1,
            "coordinator": 2,
            "hod": 3,
            "principal": 4,
            "admin": 5,
        }
        if role_hierarchy.get(role, 0) < role_hierarchy.get(required_role, 0):
            raise AuthorizationError(
                f"Role '{role}' cannot perform this action. Required: '{required_role}'"
            )
        return role
    return role_checker


async def get_db_session():
    async for session in get_db():
        yield session
