import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, require_role
from app.infrastructure.database.models import (
    TimetableModel, TimetableEntryModel, TeacherModel, ClassroomModel,
    LaboratoryModel, SubjectAssignmentModel, TimeSlotModel,
    ConflictRecordModel, SectionModel,
)
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/insights", tags=["Insights"])


@router.get("/{timetable_id}")
async def get_timetable_insights(
    timetable_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    tt = await session.get(TimetableModel, timetable_id)
    if not tt:
        raise NotFoundError("Timetable")

    section = await session.get(SectionModel, tt.section_id)

    entries_result = await session.execute(
        select(TimetableEntryModel).where(
            TimetableEntryModel.timetable_id == timetable_id,
            TimetableEntryModel.is_active.is_(True),
        )
    )
    entries = entries_result.scalars().all()

    entry_count = len(entries)
    if entry_count == 0:
        return {"insights": [], "summary": "No entries to analyze"}

    insights = []

    teacher_entries: dict[uuid.UUID, list] = {}
    for e in entries:
        teacher_entries.setdefault(e.teacher_id, []).append(e)
    teacher_loads = {tid: len(es) for tid, es in teacher_entries.items()}
    if teacher_loads:
        loads = list(teacher_loads.values())
        avg_load = sum(loads) / len(loads)
        max_load = max(loads)
        min_load = min(loads)
        if max_load > avg_load * 1.4:
            overloaded = [tid for tid, c in teacher_loads.items() if c > avg_load * 1.4]
            teacher_names = []
            for tid in overloaded[:3]:
                t = await session.get(TeacherModel, tid)
                if t:
                    teacher_names.append(t.full_name)
            insights.append({
                "type": "unbalanced_workload",
                "severity": "high",
                "title": "Faculty workload is unbalanced",
                "description": f"Top-loaded teachers: {', '.join(teacher_names)}. "
                               f"Max load: {max_load} sessions vs avg: {avg_load:.1f}.",
                "suggestion": "Redistribute subjects among under-utilized faculty members.",
            })

    room_slot_count: dict[str, int] = {}
    lab_slot_count: dict[str, int] = {}
    for e in entries:
        if e.classroom_id:
            room_slot_count[str(e.classroom_id)] = room_slot_count.get(str(e.classroom_id), 0) + 1
        if e.laboratory_id:
            lab_slot_count[str(e.laboratory_id)] = lab_slot_count.get(str(e.laboratory_id), 0) + 1

    all_rooms = (await session.execute(select(ClassroomModel))).scalars().all()
    for room in all_rooms:
        usage = room_slot_count.get(str(room.id), 0)
        if entry_count > 0 and usage < entry_count * 0.05:
            insights.append({
                "type": "underutilized_room",
                "severity": "medium",
                "title": f"'{room.name}' is underutilized",
                "description": f"Room '{room.name}' used only {usage} times out of {entry_count} total entries.",
                "suggestion": "Consider reassigning classes to better utilize this room.",
            })

    all_labs = (await session.execute(select(LaboratoryModel))).scalars().all()
    for lab in all_labs:
        usage = lab_slot_count.get(str(lab.id), 0)
        if entry_count > 0 and usage < entry_count * 0.03:
            insights.append({
                "type": "underutilized_lab",
                "severity": "medium",
                "title": f"'{lab.name}' is underutilized",
                "description": f"Lab '{lab.name}' used only {usage} times.",
                "suggestion": "Review lab allocation or merge with other practical sessions.",
            })

    day_counts: dict[str, int] = {}
    for e in entries:
        ts = await session.get(TimeSlotModel, e.time_slot_id)
        if ts:
            day_counts[ts.day_of_week] = day_counts.get(ts.day_of_week, 0) + 1
    if day_counts:
        min_day = min(day_counts, key=day_counts.get)
        min_count = day_counts[min_day]
        total = sum(day_counts.values())
        if total > 0 and min_count / total < 0.1:
            insights.append({
                "type": "low_occupancy_day",
                "severity": "low",
                "title": f"{min_day.title()} has low occupancy",
                "description": f"Only {min_count} sessions on {min_day} ({min_count/total*100:.0f}% of weekly total).",
                "suggestion": "Distribute some sessions to improve day-wise balance.",
            })

    slots_list = list(day_counts.values())
    if len(slots_list) > 1:
        import statistics
        variance = statistics.variance(slots_list) if len(slots_list) > 1 else 0
        if variance > 20:
            insights.append({
                "type": "uneven_distribution",
                "severity": "medium",
                "title": "Uneven daily class distribution",
                "description": f"Class count varies significantly across days (variance: {variance:.1f}).",
                "suggestion": "Aim for more uniform daily distribution of classes.",
            })

    conflicts_result = await session.execute(
        select(ConflictRecordModel).where(
            ConflictRecordModel.timetable_id == timetable_id,
            ConflictRecordModel.resolved.is_(False),
        )
    )
    unresolved = conflicts_result.scalars().all()
    if unresolved:
        conflicts_by_type: dict[str, int] = {}
        for c in unresolved:
            conflicts_by_tpye = conflicts_by_type
            conflicts_by_tpye[c.conflict_type] = conflicts_by_tpye.get(c.conflict_type, 0) + 1
        top = sorted(conflicts_by_type.items(), key=lambda x: x[1], reverse=True)[:2]
        insights.append({
            "type": "unresolved_conflicts",
            "severity": "high",
            "title": f"{len(unresolved)} unresolved conflict(s) exist",
            "description": f"Top conflict types: {', '.join(f'{t}({c})' for t,c in top)}.",
            "suggestion": "Auto-resolve or manually fix remaining conflicts before publishing.",
        })

    subject_sections: dict[uuid.UUID, set[uuid.UUID]] = {}
    for e in entries:
        subject_sections.setdefault(e.subject_id, set()).add(e.section_id)
    consecutive_labs = any(
        len(sections) > 1 for subj_id, sections in subject_sections.items()
        if any(
            e.is_lab_session for e in entries if e.subject_id == subj_id
        )
    )
    section_name = section.name if section else "Unknown"
    if consecutive_labs:
        insights.append({
            "type": "consecutive_labs",
            "severity": "low",
            "title": f"Section '{section_name}' has consecutive laboratory sessions",
            "description": "Multiple lab sessions detected that may cause student fatigue.",
            "suggestion": "Space out lab sessions across different days when possible.",
        })

    score_context = ""
    if tt.quality_score is not None:
        score_context = f" Current quality score: {tt.quality_score}/100."

    summary_parts = [f"Analyzed timetable '{tt.name}' (v{tt.version}) with {entry_count} entries.{score_context}"]
    if insights:
        high = sum(1 for i in insights if i["severity"] == "high")
        medium = sum(1 for i in insights if i["severity"] == "medium")
        summary_parts.append(f"Found {len(insights)} insight(s): {high} high, {medium} medium priority.")

    return {
        "timetable_id": str(timetable_id),
        "timetable_name": tt.name,
        "entry_count": entry_count,
        "quality_score": tt.quality_score,
        "insights": insights,
        "summary": " ".join(summary_parts),
    }
