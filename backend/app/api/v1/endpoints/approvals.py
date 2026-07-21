import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, get_current_user_id, get_current_user_role, require_role
from app.infrastructure.database.models import ApprovalModel, TimetableModel
from app.core.constants import TimetableStatus, ApprovalStatus
from app.core.exceptions import NotFoundError, AuthorizationError

router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.get("")
async def list_approvals(
    status: str | None = Query(None),
    timetable_id: uuid.UUID | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(get_current_user_role),
):
    query = select(ApprovalModel).where(
        ApprovalModel.is_active.is_(True),
        ApprovalModel.deleted_at.is_(None),
    )
    if status:
        query = query.where(ApprovalModel.status == status)
    if timetable_id:
        query = query.where(ApprovalModel.timetable_id == timetable_id)
    count_query = select(func.count()).select_from(query.subquery())
    total = await session.scalar(count_query) or 0
    query = query.order_by(ApprovalModel.created_at.desc()).offset(offset).limit(limit)
    result = await session.execute(query)
    items = result.scalars().all()
    return {
        "items": [_appr_to_dict(a) for a in items],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.post("")
async def create_approval(
    timetable_id: uuid.UUID = Query(...),
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
    _: str = Depends(require_role("coordinator")),
):
    existing = await session.execute(
        select(ApprovalModel).where(
            ApprovalModel.timetable_id == timetable_id,
            ApprovalModel.is_active.is_(True),
        )
    )
    existing_approval = existing.scalar_one_or_none()
    if existing_approval:
        return _appr_to_dict(existing_approval)

    tt = await session.get(TimetableModel, timetable_id)
    if not tt:
        raise NotFoundError("Timetable not found")

    approval = ApprovalModel(
        timetable_id=timetable_id,
        status=ApprovalStatus.GENERATED,
        requested_by=uuid.UUID(user_id),
        requested_at=datetime.now(timezone.utc),
    )
    session.add(approval)
    tt.status = TimetableStatus.UNDER_REVIEW
    await session.commit()
    await session.refresh(approval)
    return _appr_to_dict(approval)


@router.post("/{approval_id}/submit-review")
async def submit_for_review(
    approval_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
    _: str = Depends(require_role("coordinator")),
):
    approval = await session.get(ApprovalModel, approval_id)
    if not approval:
        raise NotFoundError("Approval not found")
    approval.status = ApprovalStatus.UNDER_REVIEW
    approval.reviewed_by = uuid.UUID(user_id)
    approval.reviewed_at = datetime.now(timezone.utc)
    await session.commit()
    return _appr_to_dict(approval)


@router.post("/{approval_id}/approve")
async def approve_timetable(
    approval_id: uuid.UUID,
    notes: str | None = Query(None),
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
    _: str = Depends(require_role("hod")),
):
    approval = await session.get(ApprovalModel, approval_id)
    if not approval:
        raise NotFoundError("Approval not found")
    if approval.status != ApprovalStatus.UNDER_REVIEW:
        raise AuthorizationError("Can only approve timetables under review")

    approval.status = ApprovalStatus.APPROVED
    approval.approved_by = uuid.UUID(user_id)
    approval.approved_at = datetime.now(timezone.utc)
    approval.review_notes = notes

    tt = await session.get(TimetableModel, approval.timetable_id)
    if tt:
        tt.status = TimetableStatus.APPROVED

    await session.commit()
    return _appr_to_dict(approval)


@router.post("/{approval_id}/publish")
async def publish_timetable(
    approval_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
    _: str = Depends(require_role("hod")),
):
    approval = await session.get(ApprovalModel, approval_id)
    if not approval:
        raise NotFoundError("Approval not found")
    if approval.status != ApprovalStatus.APPROVED:
        raise AuthorizationError("Can only publish approved timetables")

    approval.status = ApprovalStatus.PUBLISHED
    approval.published_by = uuid.UUID(user_id)
    approval.published_at = datetime.now(timezone.utc)

    tt = await session.get(TimetableModel, approval.timetable_id)
    if tt:
        tt.status = TimetableStatus.PUBLISHED

    await session.commit()
    return _appr_to_dict(approval)


@router.post("/{approval_id}/archive")
async def archive_timetable(
    approval_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
    _: str = Depends(require_role("admin")),
):
    approval = await session.get(ApprovalModel, approval_id)
    if not approval:
        raise NotFoundError("Approval not found")

    approval.status = ApprovalStatus.ARCHIVED
    approval.archived_by = uuid.UUID(user_id)
    approval.archived_at = datetime.now(timezone.utc)

    tt = await session.get(TimetableModel, approval.timetable_id)
    if tt:
        tt.status = TimetableStatus.ARCHIVED

    await session.commit()
    return _appr_to_dict(approval)


@router.get("/{approval_id}")
async def get_approval(
    approval_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(get_current_user_role),
):
    approval = await session.get(ApprovalModel, approval_id)
    if not approval:
        raise NotFoundError("Approval not found")
    return _appr_to_dict(approval)


def _appr_to_dict(a: ApprovalModel) -> dict:
    return {
        "id": str(a.id),
        "timetable_id": str(a.timetable_id),
        "status": a.status,
        "requested_by": str(a.requested_by) if a.requested_by else None,
        "requested_at": a.requested_at.isoformat() if a.requested_at else None,
        "reviewed_by": str(a.reviewed_by) if a.reviewed_by else None,
        "reviewed_at": a.reviewed_at.isoformat() if a.reviewed_at else None,
        "review_notes": a.review_notes,
        "approved_by": str(a.approved_by) if a.approved_by else None,
        "approved_at": a.approved_at.isoformat() if a.approved_at else None,
        "published_by": str(a.published_by) if a.published_by else None,
        "published_at": a.published_at.isoformat() if a.published_at else None,
        "archived_by": str(a.archived_by) if a.archived_by else None,
        "archived_at": a.archived_at.isoformat() if a.archived_at else None,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }
