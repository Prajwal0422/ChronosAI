import uuid
from sqlalchemy import String, Integer, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

from app.infrastructure.database.base import BaseModel


class VersionSnapshotModel(BaseModel):
    __tablename__ = "version_snapshots"

    timetable_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("timetables.id"), nullable=False, index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    snapshot_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    is_restored: Mapped[bool] = mapped_column(default=False, nullable=False)
    restored_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
