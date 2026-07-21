import uuid
import copy
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, get_current_user_id, get_current_user_role, require_role
from app.infrastructure.database.models import (
    SimulationModel, TimetableModel, TimetableEntryModel,
    TeacherModel, TeacherUnavailableModel, HolidayModel,
    ClassroomModel, LaboratoryModel, SectionModel, WorkingDayModel,
    TimeSlotModel,
)
from app.core.constants import SimulationType, TimetableStatus
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.get("")
async def list_simulations(
    timetable_id: uuid.UUID | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("coordinator")),
):
    query = select(SimulationModel).where(
        SimulationModel.is_active.is_(True),
        SimulationModel.deleted_at.is_(None),
    )
    if timetable_id:
        query = query.where(SimulationModel.timetable_id == timetable_id)
    query = query.order_by(SimulationModel.created_at.desc()).offset(offset).limit(limit)
    result = await session.execute(query)
    items = result.scalars().all()
    return {
        "items": [_sim_to_dict(s) for s in items],
        "total": len(items),
        "offset": offset,
        "limit": limit,
    }


@router.post("")
async def create_simulation(
    timetable_id: uuid.UUID = Query(...),
    simulation_type: str = Query(...),
    name: str = Query(...),
    description: str | None = Query(None),
    teacher_id: uuid.UUID | None = Query(None),
    classroom_id: uuid.UUID | None = Query(None),
    laboratory_id: uuid.UUID | None = Query(None),
    holiday_date: str | None = Query(None),
    section_id: uuid.UUID | None = Query(None),
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
    _: str = Depends(require_role("coordinator")),
):
    tt = await session.get(TimetableModel, timetable_id)
    if not tt:
        raise NotFoundError("Timetable not found")

    original_entries_result = await session.execute(
        select(TimetableEntryModel).where(
            TimetableEntryModel.timetable_id == timetable_id,
            TimetableEntryModel.is_active.is_(True),
        )
    )
    original_entries = original_entries_result.scalars().all()
    original_count = len(original_entries)

    params = {
        "timetable_id": str(timetable_id),
        "simulation_type": simulation_type,
        "teacher_id": str(teacher_id) if teacher_id else None,
        "classroom_id": str(classroom_id) if classroom_id else None,
        "laboratory_id": str(laboratory_id) if laboratory_id else None,
        "holiday_date": holiday_date,
        "section_id": str(section_id) if section_id else None,
    }

    impact_lines = [f"Simulation: {name} ({simulation_type})"]
    impact_lines.append(f"Original entries: {original_count}")

    affected = 0
    if simulation_type == SimulationType.TEACHER_UNAVAILABLE and teacher_id:
        teacher = await session.get(TeacherModel, teacher_id)
        for e in original_entries:
            if e.teacher_id == teacher_id:
                affected += 1
        impact_lines.append(f"Teacher: {teacher.full_name if teacher else teacher_id}")
        impact_lines.append(f"Affected entries: {affected}")
        impact_lines.append(f"Action: Mark teacher unavailable — {affected} entries would need rescheduling.")

    elif simulation_type == SimulationType.NEW_CLASSROOM:
        impact_lines.append(f"New classroom added (capacity: 60). No entries affected directly.")
        impact_lines.append("Additional room capacity may improve future scheduling flexibility.")

    elif simulation_type == SimulationType.HOLIDAY_DECLARED and holiday_date:
        for e in original_entries:
            ts = await session.get(TimeSlotModel, e.time_slot_id)
            if ts and ts.day_of_week.lower() == holiday_date.lower():
                affected += 1
        impact_lines.append(f"Holiday affects {affected} entries on that day.")
        impact_lines.append(f"Action: {affected} entries would need rescheduling to avoid holiday.")

    elif simulation_type == SimulationType.ADDITIONAL_SECTION:
        impact_lines.append("New section added. No existing entries affected.")
        impact_lines.append("Additional time slots may be needed to accommodate new section.")

    elif simulation_type == SimulationType.FACULTY_RESIGNED and teacher_id:
        teacher = await session.get(TeacherModel, teacher_id)
        for e in original_entries:
            if e.teacher_id == teacher_id:
                affected += 1
        impact_lines.append(f"Teacher: {teacher.full_name if teacher else teacher_id}")
        impact_lines.append(f"Affected entries: {affected}")
        impact_lines.append(f"Action: All {affected} entries need reassignment to another teacher.")

    elif simulation_type == SimulationType.LABORATORY_UNAVAILABLE and laboratory_id:
        lab = await session.get(LaboratoryModel, laboratory_id)
        for e in original_entries:
            if e.laboratory_id == laboratory_id:
                affected += 1
        impact_lines.append(f"Laboratory: {lab.name if lab else laboratory_id}")
        impact_lines.append(f"Affected entries: {affected}")
        impact_lines.append(f"Action: {affected} lab sessions need alternative lab assignment.")

    impact_summary = "\n".join(impact_lines)
    simulated_score = max(0, (tt.quality_score or 80) - affected * 2)

    sim = SimulationModel(
        timetable_id=timetable_id,
        simulation_type=simulation_type,
        name=name,
        description=description,
        parameters=params,
        original_score=tt.quality_score,
        simulated_score=simulated_score,
        impact_summary=impact_summary,
        created_by=uuid.UUID(user_id),
    )
    session.add(sim)
    await session.commit()
    await session.refresh(sim)

    return _sim_to_dict(sim)


@router.get("/{simulation_id}")
async def get_simulation(
    simulation_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(get_current_user_role),
):
    sim = await session.get(SimulationModel, simulation_id)
    if not sim:
        raise NotFoundError("Simulation not found")
    return _sim_to_dict(sim)


@router.post("/{simulation_id}/apply")
async def apply_simulation(
    simulation_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
    _: str = Depends(require_role("coordinator")),
):
    sim = await session.get(SimulationModel, simulation_id)
    if not sim:
        raise NotFoundError("Simulation not found")
    if sim.applied:
        return {"success": False, "message": "Simulation already applied"}

    sim.applied = True
    sim.applied_at = datetime.now(timezone.utc)

    from app.core.constants import SimulationType
    if sim.simulation_type == SimulationType.TEACHER_UNAVAILABLE:
        teacher_id_str = sim.parameters.get("teacher_id")
        if teacher_id_str:
            uid = uuid.UUID(teacher_id_str)
            entries = await session.execute(
                select(TimetableEntryModel).where(
                    TimetableEntryModel.timetable_id == sim.timetable_id,
                    TimetableEntryModel.teacher_id == uid,
                )
            )
            for e in entries.scalars().all():
                e.is_active = False

    elif sim.simulation_type == SimulationType.HOLIDAY_DECLARED:
        holiday_date = sim.parameters.get("holiday_date")
        if holiday_date:
            entries = await session.execute(
                select(TimetableEntryModel).where(
                    TimetableEntryModel.timetable_id == sim.timetable_id,
                )
            )
            for e in entries.scalars().all():
                ts = await session.get(TimeSlotModel, e.time_slot_id)
                if ts and ts.day_of_week.lower() == holiday_date.lower():
                    e.is_active = False

    elif sim.simulation_type == SimulationType.FACULTY_RESIGNED:
        teacher_id_str = sim.parameters.get("teacher_id")
        if teacher_id_str:
            uid = uuid.UUID(teacher_id_str)
            entries = await session.execute(
                select(TimetableEntryModel).where(
                    TimetableEntryModel.timetable_id == sim.timetable_id,
                    TimetableEntryModel.teacher_id == uid,
                )
            )
            for e in entries.scalars().all():
                e.is_active = False

    elif sim.simulation_type == SimulationType.LABORATORY_UNAVAILABLE:
        lab_id_str = sim.parameters.get("laboratory_id")
        if lab_id_str:
            uid = uuid.UUID(lab_id_str)
            entries = await session.execute(
                select(TimetableEntryModel).where(
                    TimetableEntryModel.timetable_id == sim.timetable_id,
                    TimetableEntryModel.laboratory_id == uid,
                )
            )
            for e in entries.scalars().all():
                e.is_active = False

    await session.commit()

    tt = await session.get(TimetableModel, sim.timetable_id)
    if tt:
        active_entries = await session.execute(
            select(TimetableEntryModel).where(
                TimetableEntryModel.timetable_id == sim.timetable_id,
                TimetableEntryModel.is_active.is_(True),
            )
        )
        active_count = len(active_entries.scalars().all())
        tt.quality_score = sim.simulated_score
        tt.status = TimetableStatus.DRAFT

    await session.commit()
    return {"success": True, "message": "Simulation applied successfully", "remaining_entries": active_count if tt else 0}


def _sim_to_dict(sim: SimulationModel) -> dict:
    return {
        "id": str(sim.id),
        "timetable_id": str(sim.timetable_id),
        "simulation_type": sim.simulation_type,
        "name": sim.name,
        "description": sim.description,
        "parameters": sim.parameters,
        "original_score": sim.original_score,
        "simulated_score": sim.simulated_score,
        "impact_summary": sim.impact_summary,
        "applied": sim.applied,
        "applied_at": sim.applied_at.isoformat() if sim.applied_at else None,
        "created_by": str(sim.created_by) if sim.created_by else None,
        "created_at": sim.created_at.isoformat() if sim.created_at else None,
    }
