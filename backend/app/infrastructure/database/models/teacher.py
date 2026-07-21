import uuid
from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel


class TeacherModel(BaseModel):
    __tablename__ = "teachers"

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    employee_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    qualification: Mapped[str | None] = mapped_column(String(255), nullable=True)
    specialization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    max_lectures_per_day: Mapped[int] = mapped_column(Integer, default=6, nullable=False)
    max_lectures_per_week: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    max_consecutive_lectures: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    department: Mapped["DepartmentModel"] = relationship("DepartmentModel", back_populates="teachers")
    subject_assignments: Mapped[list["SubjectAssignmentModel"]] = relationship(
        "SubjectAssignmentModel", back_populates="teacher", cascade="all, delete-orphan"
    )
    timetable_entries: Mapped[list["TimetableEntryModel"]] = relationship(
        "TimetableEntryModel", back_populates="teacher", cascade="all, delete-orphan"
    )
    unavailable_slots: Mapped[list["TeacherUnavailableModel"]] = relationship(
        "TeacherUnavailableModel", back_populates="teacher", cascade="all, delete-orphan"
    )


class TeacherUnavailableModel(BaseModel):
    __tablename__ = "teacher_unavailable"

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False, index=True
    )
    day_of_week: Mapped[str] = mapped_column(String(20), nullable=False)
    start_time: Mapped[str] = mapped_column(String(10), nullable=False)
    end_time: Mapped[str] = mapped_column(String(10), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    teacher: Mapped["TeacherModel"] = relationship("TeacherModel", back_populates="unavailable_slots")
