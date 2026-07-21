import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, get_current_user_id, require_role
from app.application.dto.timetable import (
    TimetableCreateRequest,
    TimetableUpdateRequest,
    TimetableResponse,
    TimetableEntryCreateRequest,
    TimetableEntryResponse,
)
from app.application.services.timetable_service import (
    TimetableService,
    TimetableEntryService,
    ConflictService,
)
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/timetables", tags=["Timetables"])


@router.get("")
async def list_timetables(
    section_id: uuid.UUID | None = Query(None),
    status: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = TimetableService(session)
    filters = {}
    if section_id:
        filters["section_id"] = section_id
    if status:
        filters["status"] = status
    items, total = await service.list(offset=offset, limit=limit, **filters)
    return {"items": [TimetableResponse.model_validate(t) for t in items], "total": total, "offset": offset, "limit": limit}


@router.post("", status_code=201)
async def create_timetable(
    request: TimetableCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
    _: str = Depends(require_role("coordinator")),
):
    service = TimetableService(session)
    tt = await service.create_timetable(
        section_id=uuid.UUID(request.section_id),
        academic_calendar_id=uuid.UUID(request.academic_calendar_id),
        name=request.name,
        generated_by=uuid.UUID(user_id),
    )
    return TimetableResponse.model_validate(tt)


@router.get("/{timetable_id}")
async def get_timetable(
    timetable_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    service = TimetableService(session)
    tt = await service.get_with_entries(timetable_id)
    return TimetableResponse.model_validate(tt)


@router.put("/{timetable_id}")
async def update_timetable(
    timetable_id: uuid.UUID,
    request: TimetableUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("coordinator")),
):
    service = TimetableService(session)
    updates = request.model_dump(exclude_unset=True)
    tt = await service.update(timetable_id, **updates)
    return TimetableResponse.model_validate(tt)


@router.delete("/{timetable_id}")
async def delete_timetable(
    timetable_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = TimetableService(session)
    await service.delete(timetable_id)
    return {"success": True}


@router.post("/{timetable_id}/publish")
async def publish_timetable(
    timetable_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("hod")),
):
    service = TimetableService(session)
    tt = await service.publish(timetable_id)
    return TimetableResponse.model_validate(tt)


@router.post("/{timetable_id}/archive")
async def archive_timetable(
    timetable_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    service = TimetableService(session)
    tt = await service.archive(timetable_id)
    return TimetableResponse.model_validate(tt)


# Entries
@router.get("/{timetable_id}/entries")
async def list_entries(
    timetable_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    entry_service = TimetableEntryService(session)
    items, total = await entry_service.list(timetable_id=timetable_id)
    return {"items": [TimetableEntryResponse.model_validate(e) for e in items], "total": total}


@router.post("/{timetable_id}/entries", status_code=201)
async def add_entry(
    timetable_id: uuid.UUID,
    request: TimetableEntryCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("coordinator")),
):
    entry_service = TimetableEntryService(session)
    entry = await entry_service.add_entry(
        timetable_id=timetable_id,
        time_slot_id=uuid.UUID(request.time_slot_id),
        section_id=uuid.UUID(request.section_id),
        teacher_id=uuid.UUID(request.teacher_id),
        subject_id=uuid.UUID(request.subject_id),
        classroom_id=uuid.UUID(request.classroom_id) if request.classroom_id else None,
        laboratory_id=uuid.UUID(request.laboratory_id) if request.laboratory_id else None,
        is_lab_session=request.is_lab_session,
        notes=request.notes,
    )
    return TimetableEntryResponse.model_validate(entry)


@router.put("/entries/{entry_id}")
async def update_entry(
    entry_id: uuid.UUID,
    request: TimetableEntryCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("coordinator")),
):
    entry_service = TimetableEntryService(session)
    updates = request.model_dump(exclude_unset=True)
    entry = await entry_service.update(entry_id, **updates)
    return TimetableEntryResponse.model_validate(entry)


@router.delete("/entries/{entry_id}")
async def delete_entry(
    entry_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("coordinator")),
):
    entry_service = TimetableEntryService(session)
    await entry_service.delete(entry_id)
    return {"success": True}


@router.post("/{timetable_id}/swap")
async def swap_entries(
    timetable_id: uuid.UUID,
    entry1_id: uuid.UUID = Query(...),
    entry2_id: uuid.UUID = Query(...),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("coordinator")),
):
    entry_service = TimetableEntryService(session)
    e1, e2 = await entry_service.swap_entries(entry1_id, entry2_id)
    return {
        "entry1": TimetableEntryResponse.model_validate(e1),
        "entry2": TimetableEntryResponse.model_validate(e2),
    }


@router.post("/{timetable_id}/generate")
async def generate_timetable(
    timetable_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
    _: str = Depends(require_role("coordinator")),
):
    from ai_engine.solver import TimetableSolver
    from app.application.services.constraint_service import ConstraintService
    from app.infrastructure.database.models import SectionModel, SemesterModel, DepartmentModel

    timetable_service = TimetableService(session)
    constraint_service = ConstraintService(session)
    entry_service = TimetableEntryService(session)

    tt = await timetable_service.get_with_entries(timetable_id)

    section = await session.get(SectionModel, tt.section_id)
    college_id = None
    if section:
        semester = await session.get(SemesterModel, section.semester_id)
        if semester:
            dept = await session.get(DepartmentModel, semester.department_id)
            if dept:
                college_id = dept.college_id

    constraints = []
    if college_id:
        constraints = await constraint_service.get_active_constraints(
            college_id=college_id,
        )

    solver = TimetableSolver(session)
    result = await solver.solve(tt, constraints)

    if result.get("entries"):
        for e in result["entries"]:
            await entry_service.add_entry(**e)

    score = result.get("score", 0)
    await timetable_service.update(timetable_id, quality_score=score, status="generated")

    conflict_service = ConflictService(session)
    conflicts = await conflict_service.detect_conflicts(timetable_id)

    return {
        "success": True,
        "score": score,
        "conflicts": len(conflicts),
        "timetable": TimetableResponse.model_validate(
            await timetable_service.get_by_id(timetable_id)
        ),
    }
