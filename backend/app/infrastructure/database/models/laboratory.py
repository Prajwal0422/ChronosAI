import uuid
from sqlalchemy import String, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel


class LaboratoryModel(BaseModel):
    __tablename__ = "laboratories"

    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id"), nullable=False, index=True
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    building: Mapped[str] = mapped_column(String(255), nullable=False)
    floor: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    equipment: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)

    college: Mapped["CollegeModel"] = relationship("CollegeModel", back_populates="laboratories")
    timetable_entries: Mapped[list["TimetableEntryModel"]] = relationship(
        "TimetableEntryModel", back_populates="laboratory", cascade="all, delete-orphan"
    )
