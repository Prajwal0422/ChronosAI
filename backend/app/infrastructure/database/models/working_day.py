import uuid
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel
from app.core.constants import DayOfWeek


class WorkingDayModel(BaseModel):
    __tablename__ = "working_days"

    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id"), nullable=False, index=True
    )
    day_of_week: Mapped[DayOfWeek] = mapped_column(
        String(20), nullable=False, index=True
    )
    is_working: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_half_day: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    college: Mapped["CollegeModel"] = relationship("CollegeModel", back_populates="working_days")
