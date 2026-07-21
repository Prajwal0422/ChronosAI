import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, require_role
from app.application.services.department_service import (
    AcademicCalendarService,
    WorkingDayService,
    HolidayService,
)
from app.application.dto.responses import ResponseBase
from pydantic import BaseModel, Field


class CalendarCreateRequest(BaseModel):
    college_id: str
    academic_year: str = Field(..., max_length=20)
    term_name: str = Field(..., max_length=255)
    start_date: date
    end_date: date


class CalendarResponse(ResponseBase):
    id: str
    college_id: str
    academic_year: str
    term_name: str
    start_date: date
    end_date: date
    is_active: bool


class WorkingDayCreateRequest(BaseModel):
    college_id: str
    day_of_week: str
    is_working: bool = True
    is_half_day: bool = False


class WorkingDayResponse(ResponseBase):
    id: str
    college_id: str
    day_of_week: str
    is_working: bool
    is_half_day: bool


class HolidayCreateRequest(BaseModel):
    college_id: str
    department_id: str | None = None
    date: date
    name: str = Field(..., max_length=255)
    holiday_type: str = "public"
    is_recurring: bool = False


class HolidayResponse(ResponseBase):
    id: str
    college_id: str
    department_id: str | None
    date: date
    name: str
    holiday_type: str
    is_recurring: bool


calendar_router = APIRouter(prefix="/calendar", tags=["Academic Calendar"])
working_days_router = APIRouter(prefix="/working-days", tags=["Working Days"])
holidays_router = APIRouter(prefix="/holidays", tags=["Holidays"])


# Academic Calendar endpoints
@calendar_router.get("")
async def list_calendars(
    college_id: uuid.UUID | None = Query(None),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = AcademicCalendarService(session)
    filters = {}
    if college_id:
        filters["college_id"] = college_id
    items, total = await service.list(**filters)
    return {"items": [CalendarResponse.model_validate(c) for c in items], "total": total}


@calendar_router.post("", status_code=201)
async def create_calendar(
    request: CalendarCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = AcademicCalendarService(session)
    cal = await service.create(**request.model_dump())
    return CalendarResponse.model_validate(cal)


@calendar_router.get("/{calendar_id}")
async def get_calendar(
    calendar_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = AcademicCalendarService(session)
    cal = await service.get_by_id(calendar_id)
    return CalendarResponse.model_validate(cal)


@calendar_router.put("/{calendar_id}")
async def update_calendar(
    calendar_id: uuid.UUID,
    request: CalendarCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = AcademicCalendarService(session)
    updates = request.model_dump(exclude_unset=True)
    cal = await service.update(calendar_id, **updates)
    return CalendarResponse.model_validate(cal)


@calendar_router.delete("/{calendar_id}")
async def delete_calendar(
    calendar_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = AcademicCalendarService(session)
    await service.delete(calendar_id)
    return {"success": True}


# Working Days endpoints
@working_days_router.get("")
async def list_working_days(
    college_id: uuid.UUID | None = Query(None),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = WorkingDayService(session)
    filters = {}
    if college_id:
        filters["college_id"] = college_id
    items, total = await service.list(**filters)
    return {"items": [WorkingDayResponse.model_validate(w) for w in items], "total": total}


@working_days_router.post("", status_code=201)
async def create_working_day(
    request: WorkingDayCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = WorkingDayService(session)
    wd = await service.create(**request.model_dump())
    return WorkingDayResponse.model_validate(wd)


@working_days_router.delete("/{wd_id}")
async def delete_working_day(
    wd_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = WorkingDayService(session)
    await service.delete(wd_id)
    return {"success": True}


# Holidays endpoints
@holidays_router.get("")
async def list_holidays(
    college_id: uuid.UUID | None = Query(None),
    year: int | None = Query(None),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = HolidayService(session)
    filters = {}
    if college_id:
        filters["college_id"] = college_id
    items, total = await service.list(**filters)
    return {"items": [HolidayResponse.model_validate(h) for h in items], "total": total}


@holidays_router.post("", status_code=201)
async def create_holiday(
    request: HolidayCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = HolidayService(session)
    h = await service.create(**request.model_dump())
    return HolidayResponse.model_validate(h)


@holidays_router.delete("/{holiday_id}")
async def delete_holiday(
    holiday_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = HolidayService(session)
    await service.delete(holiday_id)
    return {"success": True}
