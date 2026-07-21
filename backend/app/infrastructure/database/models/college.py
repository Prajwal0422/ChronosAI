import uuid
from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel
from app.core.constants import CollegeType


class CollegeModel(BaseModel):
    __tablename__ = "colleges"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    college_type: Mapped[CollegeType] = mapped_column(
        String(50), default=CollegeType.DEGREE, nullable=False
    )
    address: Mapped[str] = mapped_column(Text, nullable=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False)

    departments: Mapped[list["DepartmentModel"]] = relationship(
        "DepartmentModel", back_populates="college", cascade="all, delete-orphan"
    )
    classrooms: Mapped[list["ClassroomModel"]] = relationship(
        "ClassroomModel", back_populates="college", cascade="all, delete-orphan"
    )
    laboratories: Mapped[list["LaboratoryModel"]] = relationship(
        "LaboratoryModel", back_populates="college", cascade="all, delete-orphan"
    )
    time_slots: Mapped[list["TimeSlotModel"]] = relationship(
        "TimeSlotModel", back_populates="college", cascade="all, delete-orphan"
    )
    working_days: Mapped[list["WorkingDayModel"]] = relationship(
        "WorkingDayModel", back_populates="college", cascade="all, delete-orphan"
    )
    holidays: Mapped[list["HolidayModel"]] = relationship(
        "HolidayModel", back_populates="college", cascade="all, delete-orphan"
    )
    academic_calendars: Mapped[list["AcademicCalendarModel"]] = relationship(
        "AcademicCalendarModel", back_populates="college", cascade="all, delete-orphan"
    )
