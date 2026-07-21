import uuid
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, require_role
from app.infrastructure.database.models import (
    TimetableModel, TimetableEntryModel, TeacherModel, ClassroomModel,
    LaboratoryModel, TimeSlotModel, ConflictRecordModel, ConstraintModel,
)
from app.core.constants import ConstraintType
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/health-score", tags=["Health Score"])


def _letter_grade(score: float) -> str:
    if score >= 95: return "A+"
    if score >= 88: return "A"
    if score >= 80: return "B+"
    if score >= 70: return "B"
    if score >= 60: return "C+"
    if score >= 50: return "C"
    if score >= 40: return "D"
    return "F"


@router.get("/{timetable_id}")
async def get_health_score(
    timetable_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    tt = await session.get(TimetableModel, timetable_id)
    if not tt:
        raise NotFoundError("Timetable")

    entries_result = await session.execute(
        select(TimetableEntryModel).where(
            TimetableEntryModel.timetable_id == timetable_id,
            TimetableEntryModel.is_active.is_(True),
        )
    )
    entries = entries_result.scalars().all()
    entry_count = len(entries)

    teacher_ids = set(e.teacher_id for e in entries)
    room_ids = set(e.classroom_id for e in entries if e.classroom_id)
    lab_ids = set(e.laboratory_id for e in entries if e.laboratory_id)
    time_slot_ids = set(e.time_slot_id for e in entries)

    constraints_result = await session.execute(
        select(ConstraintModel).where(
            ConstraintModel.is_active.is_(True),
        )
    )
    all_constraints = constraints_result.scalars().all()
    hard_count = sum(1 for c in all_constraints if c.constraint_type == ConstraintType.HARD)
    soft_count = sum(1 for c in all_constraints if c.constraint_type == ConstraintType.SOFT)
    total_constraints = hard_count + soft_count

    metric_scores: dict[str, float] = {}

    if entry_count == 0:
        base_metrics = {
            "constraint_satisfaction": 100.0,
            "faculty_satisfaction": 100.0,
            "student_convenience": 100.0,
            "room_efficiency": 100.0,
            "department_balance": 100.0,
            "conflict_risk": 100.0,
        }
        overall = 100.0
    else:
        teacher_loads: dict = {}
        for e in entries:
            teacher_loads.setdefault(e.teacher_id, 0)
            teacher_loads[e.teacher_id] += 1
        if teacher_loads:
            loads = list(teacher_loads.values())
            avg_load = sum(loads) / len(loads)
            max_load = max(loads)
            min_load = min(loads)
            load_range = max_load - min_load
            if avg_load > 0:
                fac_score = max(0, 100 - (load_range / avg_load) * 50)
            else:
                fac_score = 100
        else:
            fac_score = 100
        metric_scores["faculty_satisfaction"] = round(min(100, fac_score), 1)

        day_counts: dict[str, int] = {}
        for e in entries:
            ts = await session.get(TimeSlotModel, e.time_slot_id)
            if ts:
                day_counts[ts.day_of_week] = day_counts.get(ts.day_of_week, 0) + 1
        if day_counts:
            values = list(day_counts.values())
            variance = sum((v - sum(values)/len(values))**2 for v in values) / len(values)
            student_score = max(0, 100 - variance * 2)
        else:
            student_score = 100
        metric_scores["student_convenience"] = round(min(100, student_score), 1)

        all_rooms_count = await session.scalar(select(func.count(ClassroomModel.id))) or 1
        all_labs_count = await session.scalar(select(func.count(LaboratoryModel.id))) or 1
        total_resources = all_rooms_count + all_labs_count
        used_resources = len(room_ids) + len(lab_ids)
        room_eff = (used_resources / max(total_resources, 1)) * 100
        metric_scores["room_efficiency"] = round(min(100, room_eff * 2), 1)

        section_ids = set(e.section_id for e in entries)
        section_entries: dict = {}
        for e in entries:
            section_entries.setdefault(str(e.section_id), 0)
            section_entries[str(e.section_id)] += 1
        if section_entries:
            sec_values = list(section_entries.values())
            avg_sec = sum(sec_values) / len(sec_values)
            sec_var = sum((v - avg_sec)**2 for v in sec_values) / len(sec_values)
            dept_score = max(0, 100 - sec_var * 3)
        else:
            dept_score = 100
        metric_scores["department_balance"] = round(min(100, dept_score), 1)

        conflicts_result = await session.execute(
            select(ConflictRecordModel).where(
                ConflictRecordModel.timetable_id == timetable_id,
            )
        )
        all_conflicts = conflicts_result.scalars().all()
        total_conflicts = len(all_conflicts)
        unresolved_conflicts = sum(1 for c in all_conflicts if not c.resolved)
        if total_conflicts > 0:
            conflict_ratio = unresolved_conflicts / total_conflicts
            conflict_score = max(0, 100 - (unresolved_conflicts * 15) - (total_conflicts * 5))
        else:
            conflict_score = 100
        metric_scores["conflict_risk"] = round(min(100, conflict_score), 1)

        constraint_sat = 100.0
        if total_constraints > 0:
            penalty = total_conflicts * 2 + unresolved_conflicts * 3
            constraint_sat = max(0, 100 - penalty)
        metric_scores["constraint_satisfaction"] = round(min(100, constraint_sat), 1)

        overall = (
            metric_scores["constraint_satisfaction"] * 0.25 +
            metric_scores["faculty_satisfaction"] * 0.20 +
            metric_scores["student_convenience"] * 0.15 +
            metric_scores["room_efficiency"] * 0.15 +
            metric_scores["department_balance"] * 0.10 +
            metric_scores["conflict_risk"] * 0.15
        )

    overall = round(min(100, max(0, overall)), 1)
    grade = _letter_grade(overall)

    suggestions = []
    if metric_scores.get("constraint_satisfaction", 100) < 70:
        suggestions.append("Review hard and soft constraints to improve satisfaction.")
    if metric_scores.get("faculty_satisfaction", 100) < 70:
        suggestions.append("Redistribute teaching load for better faculty balance.")
    if metric_scores.get("student_convenience", 100) < 70:
        suggestions.append("Reduce gaps and improve daily class distribution for students.")
    if metric_scores.get("room_efficiency", 100) < 50:
        suggestions.append("Optimize classroom and lab allocation to increase utilization.")
    if metric_scores.get("department_balance", 100) < 70:
        suggestions.append("Balance section workloads for fair departmental distribution.")
    if metric_scores.get("conflict_risk", 100) < 70:
        suggestions.append("Resolve outstanding conflicts to reduce scheduling risk.")
    if not suggestions:
        suggestions.append("Timetable is in good health. Continue monitoring.")

    return {
        "timetable_id": str(timetable_id),
        "timetable_name": tt.name,
        "overall_score": overall,
        "grade": grade,
        "entry_count": entry_count,
        "metrics": metric_scores,
        "improvement_suggestions": suggestions,
    }
