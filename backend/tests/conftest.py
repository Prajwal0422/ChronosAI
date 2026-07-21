import asyncio
import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.infrastructure.database.base import Base
from app.infrastructure.database.models import *  # noqa: F401, F403
from app.core.constants import UserRole, CollegeType, SubjectType

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def user_factory(db_session: AsyncSession):
    async def _create_user(**kwargs):
        from app.core.security import hash_password
        from app.infrastructure.database.models import UserModel

        user = UserModel(
            email=kwargs.get("email", f"test_{uuid.uuid4().hex[:8]}@example.com"),
            password_hash=hash_password(kwargs.get("password", "password123")),
            full_name=kwargs.get("full_name", "Test User"),
            role=kwargs.get("role", UserRole.VIEWER),
        )
        db_session.add(user)
        await db_session.flush()
        return user

    return _create_user


@pytest_asyncio.fixture(scope="function")
async def college_factory(db_session: AsyncSession):
    async def _create_college(**kwargs):
        from app.infrastructure.database.models import CollegeModel

        college = CollegeModel(
            name=kwargs.get("name", "Test College"),
            code=kwargs.get("code", f"TC{uuid.uuid4().hex[:4].upper()}"),
            college_type=kwargs.get("college_type", CollegeType.DEGREE),
            academic_year=kwargs.get("academic_year", "2024-2025"),
        )
        db_session.add(college)
        await db_session.flush()
        return college

    return _create_college
