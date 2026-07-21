import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.repositories.base import BaseRepository
from app.infrastructure.database.models import CollegeModel
from app.application.services.base_service import BaseService


class CollegeService(BaseService):
    def __init__(self, session: AsyncSession):
        repo = BaseRepository(CollegeModel, session)
        super().__init__(repo, session)

    async def get_by_code(self, code: str) -> CollegeModel | None:
        items, _ = await self.repo.list(code=code, limit=1)
        return items[0] if items else None

    async def create_college(
        self,
        name: str,
        code: str,
        college_type: str,
        academic_year: str,
        address: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        website: str | None = None,
    ) -> CollegeModel:
        return await self.create(
            name=name,
            code=code,
            college_type=college_type,
            academic_year=academic_year,
            address=address,
            phone=phone,
            email=email,
            website=website,
        )
