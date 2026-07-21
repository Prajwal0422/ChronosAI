import uuid
from sqlalchemy import String, Date, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel
from app.core.constants import HolidayType


class HolidayModel(BaseModel):
    __tablename__ = "holidays"

    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id"), nullable=False, index=True
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    holiday_type: Mapped[HolidayType] = mapped_column(
        String(50), default=HolidayType.PUBLIC, nullable=False
    )
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    college: Mapped["CollegeModel"] = relationship("CollegeModel", back_populates="holidays")
