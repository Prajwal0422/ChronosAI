import uuid
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from sqlalchemy import select, func, delete as sa_delete, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.infrastructure.database.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, **kwargs) -> ModelType:
        converted = {}
        for key, value in kwargs.items():
            if isinstance(value, str):
                try:
                    converted[key] = uuid.UUID(value)
                except (ValueError, AttributeError):
                    converted[key] = value
            else:
                converted[key] = value
        instance = self.model(**converted)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def get(self, id: uuid.UUID | str) -> ModelType | None:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = select(self.model).where(
            self.model.id == id,
            self.model.is_active.is_(True),
            self.model.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, ids: list[uuid.UUID]) -> list[ModelType]:
        stmt = select(self.model).where(
            self.model.id.in_(ids),
            self.model.is_active.is_(True),
            self.model.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list(
        self,
        *filters,
        offset: int = 0,
        limit: int = 100,
        order_by: Any = None,
        **kwargs,
    ) -> tuple[list[ModelType], int]:
        stmt = select(self.model).where(
            self.model.is_active.is_(True),
            self.model.deleted_at.is_(None),
        )
        for filter_expr in filters:
            stmt = stmt.where(filter_expr)
        for attr, value in kwargs.items():
            if value is not None:
                if isinstance(value, str):
                    try:
                        value = uuid.UUID(value)
                    except (ValueError, AttributeError):
                        pass
                column = getattr(self.model, attr, None)
                if column is not None:
                    stmt = stmt.where(column == value)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await self.session.scalar(count_stmt) or 0

        if order_by is not None:
            stmt = stmt.order_by(order_by)
        else:
            stmt = stmt.order_by(self.model.created_at.desc())

        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        return items, total

    async def update(self, id: uuid.UUID | str, **kwargs) -> ModelType | None:
        if isinstance(id, str):
            id = uuid.UUID(id)
        kwargs.pop("id", None)
        converted = {}
        for key, value in kwargs.items():
            if isinstance(value, str):
                try:
                    converted[key] = uuid.UUID(value)
                except (ValueError, AttributeError):
                    converted[key] = value
            else:
                converted[key] = value
        converted["updated_at"] = datetime.now(timezone.utc)
        stmt = (
            sa_update(self.model)
            .where(
                self.model.id == id,
                self.model.is_active.is_(True),
                self.model.deleted_at.is_(None),
            )
            .values(**converted)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one_or_none()

    async def soft_delete(self, id: uuid.UUID | str) -> bool:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = (
            sa_update(self.model)
            .where(
                self.model.id == id,
                self.model.deleted_at.is_(None),
            )
            .values(
                is_active=False,
                deleted_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def hard_delete(self, id: uuid.UUID | str) -> bool:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = sa_delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def exists(self, **kwargs) -> bool:
        stmt = select(self.model).where(
            self.model.is_active.is_(True),
            self.model.deleted_at.is_(None),
        )
        for attr, value in kwargs.items():
            if isinstance(value, str):
                try:
                    value = uuid.UUID(value)
                except (ValueError, AttributeError):
                    pass
            stmt = stmt.where(getattr(self.model, attr) == value)
        stmt = stmt.limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def _build_query(self) -> Select:
        return select(self.model).where(
            self.model.is_active.is_(True),
            self.model.deleted_at.is_(None),
        )
