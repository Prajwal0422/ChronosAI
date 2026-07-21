import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel
from app.core.constants import SlotType, DayOfWeek


class TimeSlotModel(BaseModel):
    __tablename__ = "time_slots"

    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    day_of_week: Mapped[DayOfWeek] = mapped_column(
        String(20), nullable=False, index=True
    )
    start_time: Mapped[str] = mapped_column(String(10), nullable=False)
    end_time: Mapped[str] = mapped_column(String(10), nullable=False)
    slot_type: Mapped[SlotType] = mapped_column(
        String(20), default=SlotType.LECTURE, nullable=False
    )
    slot_group: Mapped[str | None] = mapped_column(String(50), nullable=True)

    college: Mapped["CollegeModel"] = relationship("CollegeModel", back_populates="time_slots")
    timetable_entries: Mapped[list["TimetableEntryModel"]] = relationship(
        "TimetableEntryModel", back_populates="time_slot", cascade="all, delete-orphan"
    )
