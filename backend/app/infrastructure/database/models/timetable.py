import uuid
from sqlalchemy import String, Integer, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel
from app.core.constants import TimetableStatus


class TimetableModel(BaseModel):
    __tablename__ = "timetables"

    section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sections.id"), nullable=False, index=True
    )
    academic_calendar_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("academic_calendars.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[TimetableStatus] = mapped_column(
        String(50), default=TimetableStatus.DRAFT, nullable=False
    )
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    generated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    generation_params: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, default=dict
    )

    section: Mapped["SectionModel"] = relationship("SectionModel", back_populates="timetables")
    academic_calendar: Mapped["AcademicCalendarModel"] = relationship(
        "AcademicCalendarModel", back_populates="timetables"
    )
    entries: Mapped[list["TimetableEntryModel"]] = relationship(
        "TimetableEntryModel", back_populates="timetable", cascade="all, delete-orphan"
    )
    conflicts: Mapped[list["ConflictRecordModel"]] = relationship(
        "ConflictRecordModel", back_populates="timetable", cascade="all, delete-orphan"
    )


class TimetableEntryModel(BaseModel):
    __tablename__ = "timetable_entries"

    timetable_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("timetables.id"), nullable=False, index=True
    )
    time_slot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("time_slots.id"), nullable=False, index=True
    )
    section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sections.id"), nullable=False, index=True
    )
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False, index=True
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False, index=True
    )
    classroom_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("classrooms.id"), nullable=True, index=True
    )
    laboratory_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("laboratories.id"), nullable=True, index=True
    )
    is_lab_session: Mapped[bool] = mapped_column(default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    timetable: Mapped["TimetableModel"] = relationship("TimetableModel", back_populates="entries")
    time_slot: Mapped["TimeSlotModel"] = relationship("TimeSlotModel", back_populates="timetable_entries")
    section: Mapped["SectionModel"] = relationship("SectionModel")
    teacher: Mapped["TeacherModel"] = relationship("TeacherModel", back_populates="timetable_entries")
    subject: Mapped["SubjectModel"] = relationship("SubjectModel", back_populates="timetable_entries")
    classroom: Mapped["ClassroomModel | None"] = relationship(
        "ClassroomModel", back_populates="timetable_entries"
    )
    laboratory: Mapped["LaboratoryModel | None"] = relationship(
        "LaboratoryModel", back_populates="timetable_entries"
    )
