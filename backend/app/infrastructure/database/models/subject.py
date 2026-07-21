import uuid
from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel
from app.core.constants import SubjectType


class SubjectModel(BaseModel):
    __tablename__ = "subjects"

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subject_type: Mapped[SubjectType] = mapped_column(
        String(50), default=SubjectType.THEORY, nullable=False
    )
    lectures_per_week: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_elective: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_lab: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    lab_duration: Mapped[int | None] = mapped_column(Integer, nullable=True)

    department: Mapped["DepartmentModel"] = relationship("DepartmentModel", back_populates="subjects")
    subject_assignments: Mapped[list["SubjectAssignmentModel"]] = relationship(
        "SubjectAssignmentModel", back_populates="subject", cascade="all, delete-orphan"
    )
    timetable_entries: Mapped[list["TimetableEntryModel"]] = relationship(
        "TimetableEntryModel", back_populates="subject", cascade="all, delete-orphan"
    )


class SubjectAssignmentModel(BaseModel):
    __tablename__ = "subject_assignments"

    section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sections.id"), nullable=False, index=True
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False, index=True
    )
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False, index=True
    )

    section: Mapped["SectionModel"] = relationship("SectionModel", back_populates="subject_assignments")
    subject: Mapped["SubjectModel"] = relationship("SubjectModel", back_populates="subject_assignments")
    teacher: Mapped["TeacherModel"] = relationship("TeacherModel", back_populates="subject_assignments")
