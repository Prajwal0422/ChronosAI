import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, get_current_user_role, require_role
from app.infrastructure.database.models import AuditLogModel

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("")
async def list_audit_logs(
    action: str | None = Query(None),
    entity_type: str | None = Query(None),
    user_id: uuid.UUID | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    query = select(AuditLogModel).where(
        AuditLogModel.is_active.is_(True),
        AuditLogModel.deleted_at.is_(None),
    )
    if action:
        query = query.where(AuditLogModel.action == action)
    if entity_type:
        query = query.where(AuditLogModel.entity_type == entity_type)
    if user_id:
        query = query.where(AuditLogModel.user_id == user_id)

    count_query = select(func.count()).select_from(query.subquery())
    total = await session.scalar(count_query) or 0

    query = query.order_by(desc(AuditLogModel.timestamp)).offset(offset).limit(limit)
    result = await session.execute(query)
    items = result.scalars().all()

    return {
        "items": [_log_to_dict(l) for l in items],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.get("/actions")
async def list_audit_actions(
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(get_current_user_role),
):
    result = await session.execute(
        select(AuditLogModel.action, func.count(AuditLogModel.id))
        .group_by(AuditLogModel.action)
        .order_by(desc(func.count(AuditLogModel.id)))
    )
    return {row[0]: row[1] for row in result}


@router.get("/summary")
async def audit_summary(
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("admin")),
):
    total_logs = await session.scalar(
        select(func.count(AuditLogModel.id)).where(
            AuditLogModel.is_active.is_(True),
            AuditLogModel.deleted_at.is_(None),
        )
    ) or 0

    unique_users = await session.scalar(
        select(func.count(func.distinct(AuditLogModel.user_id))).where(
            AuditLogModel.user_id.isnot(None),
        )
    ) or 0

    entity_counts = await session.execute(
        select(AuditLogModel.entity_type, func.count(AuditLogModel.id))
        .group_by(AuditLogModel.entity_type)
        .order_by(desc(func.count(AuditLogModel.id)))
    )

    return {
        "total_logs": total_logs,
        "unique_users": unique_users,
        "by_entity": {row[0]: row[1] for row in entity_counts},
    }


def _log_to_dict(l: AuditLogModel) -> dict:
    return {
        "id": str(l.id),
        "user_id": str(l.user_id) if l.user_id else None,
        "action": l.action,
        "entity_type": l.entity_type,
        "entity_id": l.entity_id,
        "changes": l.changes,
        "ip_address": l.ip_address,
        "timestamp": l.timestamp.isoformat() if l.timestamp else None,
    }
