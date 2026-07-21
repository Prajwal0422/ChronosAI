import uuid
from sqlalchemy import String, Date, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel


class AcademicCalendarModel(BaseModel):
    __tablename__ = "academic_calendars"

    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id"), nullable=False, index=True
    )
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False)
    term_name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[Date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    college: Mapped["CollegeModel"] = relationship("CollegeModel", back_populates="academic_calendars")
    timetables: Mapped[list["TimetableModel"]] = relationship(
        "TimetableModel", back_populates="academic_calendar", cascade="all, delete-orphan"
    )
