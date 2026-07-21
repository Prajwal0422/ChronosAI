import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, get_current_user_id, get_current_user_role, require_role
from app.infrastructure.database.models import NotificationModel
from app.core.exceptions import NotFoundError, AppException

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("")
async def list_notifications(
    unread_only: bool = Query(False),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    query = select(NotificationModel).where(
        NotificationModel.user_id == uuid.UUID(user_id),
        NotificationModel.is_active.is_(True),
        NotificationModel.deleted_at.is_(None),
    )
    if unread_only:
        query = query.where(NotificationModel.is_read.is_(False))
    count_query = select(func.count()).select_from(query.subquery())
    total = await session.scalar(count_query) or 0
    query = query.order_by(desc(NotificationModel.created_at)).offset(offset).limit(limit)
    result = await session.execute(query)
    items = result.scalars().all()
    return {
        "items": [_notif_to_dict(n) for n in items],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.get("/unread-count")
async def unread_count(
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    count = await session.scalar(
        select(func.count(NotificationModel.id)).where(
            NotificationModel.user_id == uuid.UUID(user_id),
            NotificationModel.is_read.is_(False),
            NotificationModel.is_active.is_(True),
        )
    ) or 0
    return {"unread_count": count}


@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    notif = await session.get(NotificationModel, notification_id)
    if not notif:
        raise NotFoundError("Notification not found")
    if notif.user_id != uuid.UUID(user_id):
        raise AppException("FORBIDDEN", "Cannot access another user's notification", status_code=403)
    notif.is_read = True
    notif.read_at = datetime.now(timezone.utc)
    await session.commit()
    return {"success": True}


@router.post("/read-all")
async def mark_all_as_read(
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    result = await session.execute(
        select(NotificationModel).where(
            NotificationModel.user_id == uuid.UUID(user_id),
            NotificationModel.is_read.is_(False),
            NotificationModel.is_active.is_(True),
        )
    )
    for notif in result.scalars().all():
        notif.is_read = True
        notif.read_at = datetime.now(timezone.utc)
    await session.commit()
    return {"success": True, "marked_count": result.rowcount}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
):
    notif = await session.get(NotificationModel, notification_id)
    if not notif:
        raise NotFoundError("Notification not found")
    if notif.user_id != uuid.UUID(user_id):
        raise AppException("FORBIDDEN", "Cannot delete another user's notification", status_code=403)
    notif.is_active = False
    await session.commit()
    return {"success": True}


async def create_notification(
    session: AsyncSession,
    user_id: uuid.UUID,
    notification_type: str,
    title: str,
    message: str,
    reference_type: str | None = None,
    reference_id: uuid.UUID | None = None,
):
    notif = NotificationModel(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        reference_type=reference_type,
        reference_id=reference_id,
    )
    session.add(notif)
    await session.commit()


def _notif_to_dict(n: NotificationModel) -> dict:
    return {
        "id": str(n.id),
        "user_id": str(n.user_id),
        "notification_type": n.notification_type,
        "title": n.title,
        "message": n.message,
        "is_read": n.is_read,
        "reference_type": n.reference_type,
        "reference_id": str(n.reference_id) if n.reference_id else None,
        "read_at": n.read_at.isoformat() if n.read_at else None,
        "created_at": n.created_at.isoformat() if n.created_at else None,
    }
