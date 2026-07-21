import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel


class DepartmentModel(BaseModel):
    __tablename__ = "departments"

    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    hod_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    college: Mapped["CollegeModel"] = relationship("CollegeModel", back_populates="departments")
    semesters: Mapped[list["SemesterModel"]] = relationship(
        "SemesterModel", back_populates="department", cascade="all, delete-orphan"
    )
    teachers: Mapped[list["TeacherModel"]] = relationship(
        "TeacherModel", back_populates="department", cascade="all, delete-orphan"
    )
    subjects: Mapped[list["SubjectModel"]] = relationship(
        "SubjectModel", back_populates="department", cascade="all, delete-orphan"
    )
