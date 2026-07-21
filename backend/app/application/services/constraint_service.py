import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.base_service import BaseService
from app.infrastructure.database.models import ConstraintModel
from app.infrastructure.database.repositories.base import BaseRepository
from app.core.exceptions import ValidationError


class ConstraintService(BaseService):
    def __init__(self, session: AsyncSession):
        repo = BaseRepository(ConstraintModel, session)
        super().__init__(repo, session)
        self.session = session

    async def get_active_constraints(
        self, college_id: uuid.UUID, department_id: uuid.UUID | None = None
    ) -> list[ConstraintModel]:
        filters = {"college_id": college_id, "is_active": True}
        if department_id:
            items1, _ = await self.repo.list(college_id=college_id, department_id=department_id, is_active=True)
            items2, _ = await self.repo.list(college_id=college_id, department_id=None, is_active=True)
            return items1 + items2
        items, _ = await self.repo.list(**filters)
        return items

    async def validate_constraint_config(
        self, constraint_type: str, category: str, config: dict
    ) -> bool:
        required_fields = {
            "teacher": ["teacher_id"] if constraint_type == "hard" else [],
            "room": ["room_id"],
            "time": ["day_of_week", "start_time", "end_time"],
        }
        fields = required_fields.get(category, [])
        for field in fields:
            if field not in config:
                raise ValidationError(
                    f"Missing required field '{field}' for {category} constraint"
                )
        return True
