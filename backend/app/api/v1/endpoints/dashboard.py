from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, get_current_user_id, require_role
from app.infrastructure.database.models import (
    TimetableModel,
    ConflictRecordModel,
    TeacherModel,
    SubjectAssignmentModel,
)
from app.core.constants import TimetableStatus

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
async def get_dashboard_summary(
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
    role: str = Depends(require_role("viewer")),
):
    tt_count = await session.scalar(
        select(func.count(TimetableModel.id)).where(
            TimetableModel.is_active.is_(True),
            TimetableModel.deleted_at.is_(None),
        )
    ) or 0

    conflict_count = await session.scalar(
        select(func.count(ConflictRecordModel.id)).where(
            ConflictRecordModel.resolved.is_(False),
        )
    ) or 0

    teacher_count = await session.scalar(
        select(func.count(TeacherModel.id)).where(
            TeacherModel.is_active.is_(True),
            TeacherModel.deleted_at.is_(None),
        )
    ) or 0

    assignment_count = await session.scalar(
        select(func.count(SubjectAssignmentModel.id))
    ) or 0

    avg_quality = await session.scalar(
        select(func.avg(TimetableModel.quality_score)).where(
            TimetableModel.quality_score.isnot(None),
            TimetableModel.is_active.is_(True),
            TimetableModel.deleted_at.is_(None),
        )
    ) or 0

    return {
        "total_timetables": tt_count,
        "active_conflicts": conflict_count,
        "total_teachers": teacher_count,
        "total_assignments": assignment_count,
        "avg_quality_score": round(float(avg_quality), 1),
        "role": role,
    }


@router.get("/recent-activity")
async def get_recent_activity(
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(get_current_user_id),
):
    from app.infrastructure.database.models import AuditLogModel
    stmt = (
        select(AuditLogModel)
        .where(AuditLogModel.deleted_at.is_(None))
        .order_by(AuditLogModel.timestamp.desc())
        .limit(10)
    )
    result = await session.execute(stmt)
    logs = list(result.scalars().all())
    return {
        "activities": [
            {
                "action": log.action,
                "entity_type": log.entity_type,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            }
            for log in logs
        ]
    }
