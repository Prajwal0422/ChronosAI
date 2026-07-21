import uuid

import pytest
import pytest_asyncio

from app.infrastructure.database.repositories.base import BaseRepository
from app.infrastructure.database.models import UserModel, CollegeModel
from app.core.constants import UserRole, CollegeType


@pytest.mark.asyncio
class TestBaseRepository:
    async def test_create(self, db_session, user_factory):
        user = await user_factory()
        repo = BaseRepository(UserModel, db_session)
        fetched = await repo.get(user.id)
        assert fetched is not None
        assert fetched.id == user.id
        assert fetched.email == user.email

    async def test_get_not_found(self, db_session):
        repo = BaseRepository(UserModel, db_session)
        fake_id = uuid.uuid4()
        result = await repo.get(fake_id)
        assert result is None

    async def test_list(self, db_session, user_factory):
        await user_factory(email="user1@example.com")
        await user_factory(email="user2@example.com")

        repo = BaseRepository(UserModel, db_session)
        items, total = await repo.list()
        assert total >= 2
        assert len(items) >= 2

    async def test_list_with_filter(self, db_session, user_factory):
        await user_factory(email="user1@example.com", role=UserRole.ADMIN)
        await user_factory(email="user2@example.com", role=UserRole.FACULTY)

        repo = BaseRepository(UserModel, db_session)
        items, total = await repo.list(role=UserRole.ADMIN.value)
        assert total >= 1
        for item in items:
            assert item.role == UserRole.ADMIN.value

    async def test_update(self, db_session, user_factory):
        user = await user_factory(full_name="Original Name")
        repo = BaseRepository(UserModel, db_session)
        updated = await repo.update(user.id, full_name="Updated Name")
        assert updated is not None
        assert updated.full_name == "Updated Name"

    async def test_update_not_found(self, db_session):
        repo = BaseRepository(UserModel, db_session)
        result = await repo.update(uuid.uuid4(), full_name="Test")
        assert result is None

    async def test_soft_delete(self, db_session, user_factory):
        user = await user_factory()
        repo = BaseRepository(UserModel, db_session)
        result = await repo.soft_delete(user.id)
        assert result is True

        fetched = await repo.get(user.id)
        assert fetched is None

    async def test_exists(self, db_session, user_factory):
        user = await user_factory(email="exists@example.com")
        repo = BaseRepository(UserModel, db_session)
        assert await repo.exists(email="exists@example.com") is True
        assert await repo.exists(email="nonexistent@example.com") is False
