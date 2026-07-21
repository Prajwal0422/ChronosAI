import uuid
from collections import defaultdict
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, require_role
from app.infrastructure.database.models import (
    TimetableModel, ConflictRecordModel, TeacherModel, ClassroomModel,
    LaboratoryModel, TimetableEntryModel, SubjectAssignmentModel,
    TimeSlotModel, SectionModel, DepartmentModel,
)
from app.core.constants import TimetableStatus

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview")
async def analytics_overview(
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    total_tt = await session.scalar(
        select(func.count(TimetableModel.id)).where(
            TimetableModel.is_active.is_(True),
            TimetableModel.deleted_at.is_(None),
        )
    ) or 0

    published_tt = await session.scalar(
        select(func.count(TimetableModel.id)).where(
            TimetableModel.status == TimetableStatus.PUBLISHED,
            TimetableModel.is_active.is_(True),
        )
    ) or 0

    avg_score = await session.scalar(
        select(func.avg(TimetableModel.quality_score)).where(
            TimetableModel.quality_score.isnot(None),
        )
    ) or 0

    total_conflicts = await session.scalar(
        select(func.count(ConflictRecordModel.id))
    ) or 0

    resolved_conflicts = await session.scalar(
        select(func.count(ConflictRecordModel.id)).where(
            ConflictRecordModel.resolved.is_(True),
        )
    ) or 0

    total_entries = await session.scalar(
        select(func.count(TimetableEntryModel.id))
    ) or 0

    total_teachers = await session.scalar(
        select(func.count(TeacherModel.id)).where(
            TeacherModel.is_active.is_(True),
            TeacherModel.deleted_at.is_(None),
        )
    ) or 0

    return {
        "total_timetables": total_tt,
        "published_timetables": published_tt,
        "average_quality_score": round(float(avg_score), 2),
        "total_conflicts": total_conflicts,
        "resolved_conflicts": resolved_conflicts,
        "conflict_resolution_rate": round(resolved_conflicts / total_conflicts * 100, 2) if total_conflicts > 0 else 0,
        "total_entries": total_entries,
        "total_teachers": total_teachers,
    }


@router.get("/conflicts")
async def conflict_analytics(
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    from app.core.constants import ConflictType

    conflict_types = await session.execute(
        select(ConflictRecordModel.conflict_type, func.count(ConflictRecordModel.id))
        .group_by(ConflictRecordModel.conflict_type)
    )
    type_counts = {row[0]: row[1] for row in conflict_types}

    return {
        "by_type": type_counts,
        "total": sum(type_counts.values()),
    }


@router.get("/faculty-workload")
async def faculty_workload(
    department_id: uuid.UUID | None = Query(None),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    tq = select(TeacherModel).where(
        TeacherModel.is_active.is_(True),
        TeacherModel.deleted_at.is_(None),
    )
    if department_id:
        tq = tq.where(TeacherModel.department_id == department_id)
    teachers = (await session.execute(tq)).scalars().all()

    workload = []
    for t in teachers:
        entry_count = await session.scalar(
            select(func.count(TimetableEntryModel.id)).where(
                TimetableEntryModel.teacher_id == t.id,
                TimetableEntryModel.is_active.is_(True),
            )
        ) or 0
        workload.append({
            "teacher_id": str(t.id),
            "full_name": t.full_name,
            "employee_code": t.employee_code,
            "department_id": str(t.department_id),
            "total_entries": entry_count,
            "max_weekly": t.max_lectures_per_week,
            "utilization_pct": round((entry_count / max(t.max_lectures_per_week, 1)) * 100, 1),
        })

    workload.sort(key=lambda x: x["total_entries"], reverse=True)
    return {"items": workload, "total": len(workload)}


@router.get("/department-utilization")
async def department_utilization(
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    depts = (await session.execute(
        select(DepartmentModel).where(
            DepartmentModel.is_active.is_(True),
            DepartmentModel.deleted_at.is_(None),
        )
    )).scalars().all()

    result = []
    for d in depts:
        teacher_count = await session.scalar(
            select(func.count(TeacherModel.id)).where(
                TeacherModel.department_id == d.id,
                TeacherModel.is_active.is_(True),
            )
        ) or 0
        subject_count = await session.scalar(
            select(func.count(SubjectAssignmentModel.id)).where(
                SubjectAssignmentModel.section_id.in_(
                    select(SectionModel.id).where(
                        SectionModel.semester_id.in_(
                            select(SemesterModel).where(
                                SemesterModel.department_id == d.id,
                                SemesterModel.is_active.is_(True),
                            ).subquery()
                        )
                    )
                )
            )
        ) or 0
        entry_count = await session.scalar(
            select(func.count(TimetableEntryModel.id)).where(
                TimetableEntryModel.section_id.in_(
                    select(SectionModel.id).where(
                        SectionModel.is_active.is_(True),
                        SectionModel.deleted_at.is_(None),
                    )
                )
            )
        ) or 0
        result.append({
            "department_id": str(d.id),
            "name": d.name,
            "code": d.code,
            "teacher_count": teacher_count,
            "subject_assignment_count": subject_count,
            "total_entries": entry_count,
        })

    return {"items": result, "total": len(result)}


@router.get("/room-utilization")
async def room_utilization(
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    rooms = (await session.execute(
        select(ClassroomModel).where(
            ClassroomModel.is_active.is_(True),
            ClassroomModel.deleted_at.is_(None),
        )
    )).scalars().all()

    result = []
    for r in rooms:
        usage_count = await session.scalar(
            select(func.count(TimetableEntryModel.id)).where(
                TimetableEntryModel.classroom_id == r.id,
                TimetableEntryModel.is_active.is_(True),
            )
        ) or 0
        result.append({
            "room_id": str(r.id),
            "name": r.name,
            "code": r.code,
            "capacity": r.capacity,
            "building": r.building,
            "usage_count": usage_count,
            "utilization_pct": round(min(100, (usage_count / 40) * 100), 1),
        })

    result.sort(key=lambda x: x["usage_count"], reverse=True)
    return {"items": result, "total": len(result)}


@router.get("/lab-utilization")
async def lab_utilization(
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    labs = (await session.execute(
        select(LaboratoryModel).where(
            LaboratoryModel.is_active.is_(True),
            LaboratoryModel.deleted_at.is_(None),
        )
    )).scalars().all()

    result = []
    for l in labs:
        usage_count = await session.scalar(
            select(func.count(TimetableEntryModel.id)).where(
                TimetableEntryModel.laboratory_id == l.id,
                TimetableEntryModel.is_active.is_(True),
            )
        ) or 0
        result.append({
            "lab_id": str(l.id),
            "name": l.name,
            "code": l.code,
            "capacity": l.capacity,
            "usage_count": usage_count,
            "utilization_pct": round(min(100, (usage_count / 30) * 100), 1),
        })

    result.sort(key=lambda x: x["usage_count"], reverse=True)
    return {"items": result, "total": len(result)}


@router.get("/weekly-hours")
async def weekly_hours(
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    teachers = (await session.execute(
        select(TeacherModel).where(
            TeacherModel.is_active.is_(True),
            TeacherModel.deleted_at.is_(None),
        )
    )).scalars().all()

    hours_data = []
    for t in teachers:
        entries = (await session.execute(
            select(TimetableEntryModel).where(
                TimetableEntryModel.teacher_id == t.id,
                TimetableEntryModel.is_active.is_(True),
            )
        )).scalars().all()
        total_minutes = 0
        for e in entries:
            ts = await session.get(TimeSlotModel, e.time_slot_id)
            if ts:
                start_h, start_m = ts.start_time.split(":")
                end_h, end_m = ts.end_time.split(":")
                total_minutes += (int(end_h) * 60 + int(end_m)) - (int(start_h) * 60 + int(start_m))
        hours_data.append({
            "teacher_id": str(t.id),
            "full_name": t.full_name,
            "weekly_hours": round(total_minutes / 60, 1),
            "max_weekly": t.max_lectures_per_week,
        })

    hours_data.sort(key=lambda x: x["weekly_hours"], reverse=True)
    return {"items": hours_data, "total": len(hours_data)}


@router.get("/daily-occupancy")
async def daily_occupancy(
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    days_order = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    day_counts = {d: 0 for d in days_order}

    entries = (await session.execute(
        select(TimetableEntryModel).where(
            TimetableEntryModel.is_active.is_(True),
        )
    )).scalars().all()

    for e in entries:
        ts = await session.get(TimeSlotModel, e.time_slot_id)
        if ts and ts.day_of_week.lower() in day_counts:
            day_counts[ts.day_of_week.lower()] += 1

    result = []
    for day in days_order:
        if day_counts[day] > 0:
            result.append({"day": day, "count": day_counts[day], "occupancy_pct": 0})

    total = sum(day_counts.values())
    for item in result:
        item["occupancy_pct"] = round((item["count"] / max(total, 1)) * 100, 1)

    return {"items": result, "total_entries": total}


@router.get("/class-distribution")
async def class_distribution(
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    time_slots = (await session.execute(
        select(TimeSlotModel).where(
            TimeSlotModel.is_active.is_(True),
            TimeSlotModel.deleted_at.is_(None),
        )
    )).scalars().all()

    slot_entry_counts: dict = {}
    for ts in time_slots:
        count = await session.scalar(
            select(func.count(TimetableEntryModel.id)).where(
                TimetableEntryModel.time_slot_id == ts.id,
                TimetableEntryModel.is_active.is_(True),
            )
        ) or 0
        slot_entry_counts[f"{ts.day_of_week}_{ts.start_time}"] = {
            "day": ts.day_of_week,
            "start_time": ts.start_time,
            "end_time": ts.end_time,
            "count": count,
        }

    return {"items": list(slot_entry_counts.values())}


@router.get("/resource-usage")
async def resource_usage(
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    total_rooms = await session.scalar(
        select(func.count(ClassroomModel.id)).where(
            ClassroomModel.is_active.is_(True),
            ClassroomModel.deleted_at.is_(None),
        )
    ) or 1
    total_labs = await session.scalar(
        select(func.count(LaboratoryModel.id)).where(
            LaboratoryModel.is_active.is_(True),
            LaboratoryModel.deleted_at.is_(None),
        )
    ) or 1

    rooms_used = await session.scalar(
        select(func.count(func.distinct(TimetableEntryModel.classroom_id))).where(
            TimetableEntryModel.classroom_id.isnot(None),
            TimetableEntryModel.is_active.is_(True),
        )
    ) or 0
    labs_used = await session.scalar(
        select(func.count(func.distinct(TimetableEntryModel.laboratory_id))).where(
            TimetableEntryModel.laboratory_id.isnot(None),
            TimetableEntryModel.is_active.is_(True),
        )
    ) or 0

    return {
        "total_rooms": total_rooms,
        "rooms_used": rooms_used,
        "room_usage_pct": round((rooms_used / total_rooms) * 100, 1),
        "total_labs": total_labs,
        "labs_used": labs_used,
        "lab_usage_pct": round((labs_used / total_labs) * 100, 1),
        "overall_usage_pct": round(((rooms_used + labs_used) / max(total_rooms + total_labs, 1)) * 100, 1),
    }
