import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, get_current_user_id, require_role
from app.infrastructure.database.models import (
    VersionSnapshotModel, TimetableModel, TimetableEntryModel,
)
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/versions", tags=["Versions"])


@router.get("")
async def list_versions(
    timetable_id: uuid.UUID | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("coordinator")),
):
    query = select(VersionSnapshotModel).where(
        VersionSnapshotModel.is_active.is_(True),
        VersionSnapshotModel.deleted_at.is_(None),
    )
    if timetable_id:
        query = query.where(VersionSnapshotModel.timetable_id == timetable_id)
    count_query = select(func.count()).select_from(query.subquery())
    total = await session.scalar(count_query) or 0
    query = query.order_by(VersionSnapshotModel.version_number.desc()).offset(offset).limit(limit)
    result = await session.execute(query)
    items = result.scalars().all()
    return {
        "items": [_ver_to_dict(v) for v in items],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.post("")
async def create_version_snapshot(
    timetable_id: uuid.UUID = Query(...),
    label: str | None = Query(None),
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
    _: str = Depends(require_role("coordinator")),
):
    tt = await session.get(TimetableModel, timetable_id)
    if not tt:
        raise NotFoundError("Timetable not found")

    entries_result = await session.execute(
        select(TimetableEntryModel).where(
            TimetableEntryModel.timetable_id == timetable_id,
            TimetableEntryModel.is_active.is_(True),
        )
    )
    entries = entries_result.scalars().all()

    entries_data = []
    for e in entries:
        entries_data.append({
            "id": str(e.id),
            "time_slot_id": str(e.time_slot_id),
            "section_id": str(e.section_id),
            "teacher_id": str(e.teacher_id),
            "subject_id": str(e.subject_id),
            "classroom_id": str(e.classroom_id) if e.classroom_id else None,
            "laboratory_id": str(e.laboratory_id) if e.laboratory_id else None,
            "is_lab_session": e.is_lab_session,
            "notes": e.notes,
        })

    max_ver_result = await session.execute(
        select(func.max(VersionSnapshotModel.version_number)).where(
            VersionSnapshotModel.timetable_id == timetable_id,
        )
    )
    max_ver = max_ver_result.scalar() or 0
    new_version = max_ver + 1

    snapshot = VersionSnapshotModel(
        timetable_id=timetable_id,
        version_number=new_version,
        label=label or f"Version {new_version}",
        snapshot_data={
            "timetable": {
                "id": str(tt.id),
                "name": tt.name,
                "section_id": str(tt.section_id),
                "version": tt.version,
                "status": tt.status.value if hasattr(tt.status, 'value') else tt.status,
            },
            "entries": entries_data,
        },
        quality_score=tt.quality_score,
        change_summary=f"Snapshot v{new_version}: {len(entries)} entries",
        created_by=uuid.UUID(user_id),
    )
    session.add(snapshot)
    await session.commit()
    await session.refresh(snapshot)

    return _ver_to_dict(snapshot)


@router.get("/{version_id}")
async def get_version(
    version_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("coordinator")),
):
    ver = await session.get(VersionSnapshotModel, version_id)
    if not ver:
        raise NotFoundError("Version not found")
    return _ver_to_dict(ver)


@router.post("/{version_id}/restore")
async def restore_version(
    version_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
    _: str = Depends(require_role("coordinator")),
):
    ver = await session.get(VersionSnapshotModel, version_id)
    if not ver:
        raise NotFoundError("Version not found")

    tt = await session.get(TimetableModel, ver.timetable_id)
    if not tt:
        raise NotFoundError("Timetable not found")

    existing_entries = await session.execute(
        select(TimetableEntryModel).where(
            TimetableEntryModel.timetable_id == ver.timetable_id,
        )
    )
    for e in existing_entries.scalars().all():
        await session.delete(e)

    entries_data = ver.snapshot_data.get("entries", [])
    for ed in entries_data:
        new_entry = TimetableEntryModel(
            timetable_id=ver.timetable_id,
            time_slot_id=uuid.UUID(ed["time_slot_id"]),
            section_id=uuid.UUID(ed["section_id"]),
            teacher_id=uuid.UUID(ed["teacher_id"]),
            subject_id=uuid.UUID(ed["subject_id"]),
            classroom_id=uuid.UUID(ed["classroom_id"]) if ed.get("classroom_id") else None,
            laboratory_id=uuid.UUID(ed["laboratory_id"]) if ed.get("laboratory_id") else None,
            is_lab_session=ed.get("is_lab_session", False),
            notes=ed.get("notes"),
        )
        session.add(new_entry)

    tt.quality_score = ver.quality_score
    tt.version = ver.version_number

    ver.is_restored = True
    ver.restored_at = datetime.now(timezone.utc)

    await session.commit()

    return {
        "success": True,
        "message": f"Restored version {ver.version_number} ({len(entries_data)} entries)",
        "timetable_id": str(ver.timetable_id),
        "version_number": ver.version_number,
    }


@router.post("/compare")
async def compare_versions(
    version_id_1: uuid.UUID = Query(...),
    version_id_2: uuid.UUID = Query(...),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("coordinator")),
):
    v1 = await session.get(VersionSnapshotModel, version_id_1)
    v2 = await session.get(VersionSnapshotModel, version_id_2)
    if not v1 or not v2:
        raise NotFoundError("One or both versions not found")

    entries_1 = {(e["time_slot_id"], e["section_id"], e["teacher_id"])
                 for e in v1.snapshot_data.get("entries", [])}
    entries_2 = {(e["time_slot_id"], e["section_id"], e["teacher_id"])
                 for e in v2.snapshot_data.get("entries", [])}

    added = len(entries_2 - entries_1)
    removed = len(entries_1 - entries_2)
    common = len(entries_1 & entries_2)
    total_1 = len(entries_1)
    total_2 = len(entries_2)
    score_1 = v1.quality_score or 0
    score_2 = v2.quality_score or 0

    changes = []
    if added > 0:
        changes.append(f"{added} entries added")
    if removed > 0:
        changes.append(f"{removed} entries removed")
    if common < max(total_1, total_2):
        changes.append(f"{total_2 - common} entries modified")
    if score_2 != score_1:
        direction = "improved" if score_2 > score_1 else "decreased"
        changes.append(f"Score {direction}: {score_1} → {score_2}")

    return {
        "version_1": {"number": v1.version_number, "score": score_1, "entries": total_1, "label": v1.label},
        "version_2": {"number": v2.version_number, "score": score_2, "entries": total_2, "label": v2.label},
        "added": added,
        "removed": removed,
        "common": common,
        "score_change": round(score_2 - score_1, 1),
        "change_summary": "; ".join(changes) if changes else "No significant differences",
    }


def _ver_to_dict(v: VersionSnapshotModel) -> dict:
    return {
        "id": str(v.id),
        "timetable_id": str(v.timetable_id),
        "version_number": v.version_number,
        "label": v.label,
        "quality_score": v.quality_score,
        "entry_count": len(v.snapshot_data.get("entries", [])),
        "change_summary": v.change_summary,
        "is_restored": v.is_restored,
        "restored_at": v.restored_at.isoformat() if v.restored_at else None,
        "created_by": str(v.created_by) if v.created_by else None,
        "created_at": v.created_at.isoformat() if v.created_at else None,
    }
