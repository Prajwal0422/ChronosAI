import uuid
from typing import Any, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.repositories.base import BaseRepository
from app.infrastructure.database.base import BaseModel
from app.core.exceptions import NotFoundError, BusinessRuleError

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseService:
    def __init__(self, repository: BaseRepository, session: AsyncSession):
        self.repo = repository
        self.session = session
        self.entity_name = repository.model.__name__.replace("Model", "")

    async def get_by_id(self, id: uuid.UUID) -> BaseModel:
        entity = await self.repo.get(id)
        if not entity:
            raise NotFoundError(self.entity_name, str(id))
        return entity

    async def list(
        self,
        offset: int = 0,
        limit: int = 100,
        order_by: Any = None,
        **filters,
    ) -> tuple[list[BaseModel], int]:
        return await self.repo.list(
            offset=offset, limit=limit, order_by=order_by, **filters
        )

    async def create(self, **kwargs) -> BaseModel:
        return await self.repo.create(**kwargs)

    async def update(self, id: uuid.UUID, **kwargs) -> BaseModel:
        entity = await self.repo.update(id, **kwargs)
        if not entity:
            raise NotFoundError(self.entity_name, str(id))
        return entity

    async def delete(self, id: uuid.UUID) -> bool:
        entity = await self.repo.get(id)
        if not entity:
            raise NotFoundError(self.entity_name, str(id))
        return await self.repo.soft_delete(id)

    async def exists(self, **kwargs) -> bool:
        return await self.repo.exists(**kwargs)
