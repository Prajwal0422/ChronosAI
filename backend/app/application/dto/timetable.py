from pydantic import BaseModel, Field
from app.application.dto.responses import ResponseBase


class TimetableCreateRequest(BaseModel):
    section_id: str
    academic_calendar_id: str
    name: str = Field(..., min_length=1, max_length=255)


class TimetableUpdateRequest(BaseModel):
    name: str | None = Field(None, max_length=255)
    status: str | None = None


class TimetableResponse(ResponseBase):
    id: str
    section_id: str
    academic_calendar_id: str
    name: str
    version: int
    status: str
    quality_score: float | None
    is_active: bool


class TimetableEntryCreateRequest(BaseModel):
    timetable_id: str | None = None
    time_slot_id: str
    section_id: str
    teacher_id: str
    subject_id: str
    classroom_id: str | None = None
    laboratory_id: str | None = None
    is_lab_session: bool = False
    notes: str | None = Field(None, max_length=500)


class TimetableEntryResponse(ResponseBase):
    id: str
    timetable_id: str
    time_slot_id: str
    section_id: str
    teacher_id: str
    subject_id: str
    classroom_id: str | None
    laboratory_id: str | None
    is_lab_session: bool
    notes: str | None
