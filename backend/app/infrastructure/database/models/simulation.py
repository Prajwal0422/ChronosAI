import uuid
from sqlalchemy import String, Text, Float, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

from app.infrastructure.database.base import BaseModel


class SimulationModel(BaseModel):
    __tablename__ = "simulations"

    timetable_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("timetables.id"), nullable=False, index=True
    )
    simulation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parameters: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    original_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    simulated_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    impact_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    diff_entries: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    applied: Mapped[bool] = mapped_column(default=False, nullable=False)
    applied_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
