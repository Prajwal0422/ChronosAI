import uuid
from sqlalchemy import String, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel
from app.core.constants import ConflictType, ConflictSeverity


class ConflictRecordModel(BaseModel):
    __tablename__ = "conflict_records"

    timetable_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("timetables.id"), nullable=False, index=True
    )
    conflict_type: Mapped[ConflictType] = mapped_column(
        String(50), nullable=False, index=True
    )
    severity: Mapped[ConflictSeverity] = mapped_column(
        String(20), nullable=False, default=ConflictSeverity.MEDIUM
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    involved_entries: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    resolved_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    timetable: Mapped["TimetableModel"] = relationship("TimetableModel", back_populates="conflicts")
