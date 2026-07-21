import uuid
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel


class SectionModel(BaseModel):
    __tablename__ = "sections"

    semester_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("semesters.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    strength: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    semester: Mapped["SemesterModel"] = relationship("SemesterModel", back_populates="sections")
    subject_assignments: Mapped[list["SubjectAssignmentModel"]] = relationship(
        "SubjectAssignmentModel", back_populates="section", cascade="all, delete-orphan"
    )
    timetables: Mapped[list["TimetableModel"]] = relationship(
        "TimetableModel", back_populates="section", cascade="all, delete-orphan"
    )
