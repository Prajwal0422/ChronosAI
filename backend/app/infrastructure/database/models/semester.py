import uuid
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel


class SemesterModel(BaseModel):
    __tablename__ = "semesters"

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    department: Mapped["DepartmentModel"] = relationship("DepartmentModel", back_populates="semesters")
    sections: Mapped[list["SectionModel"]] = relationship(
        "SectionModel", back_populates="semester", cascade="all, delete-orphan"
    )
