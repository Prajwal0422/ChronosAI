import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.services.base_service import BaseService
from app.infrastructure.database.models import (
    TimetableModel,
    TimetableEntryModel,
    ConflictRecordModel,
    SubjectAssignmentModel,
)
from app.infrastructure.database.repositories.base import BaseRepository
from app.core.exceptions import NotFoundError, BusinessRuleError
from app.core.constants import TimetableStatus, ConflictType, ConflictSeverity


class TimetableService(BaseService):
    def __init__(self, session: AsyncSession):
        repo = BaseRepository(TimetableModel, session)
        super().__init__(repo, session)
        self.session = session

    async def create_timetable(
        self,
        section_id: uuid.UUID,
        academic_calendar_id: uuid.UUID,
        name: str,
        generated_by: uuid.UUID | None = None,
    ) -> TimetableModel:
        return await self.create(
            section_id=section_id,
            academic_calendar_id=academic_calendar_id,
            name=name,
            status=TimetableStatus.DRAFT,
            version=1,
            generated_by=generated_by,
        )

    async def get_with_entries(self, timetable_id: uuid.UUID) -> TimetableModel:
        stmt = (
            select(TimetableModel)
            .where(
                TimetableModel.id == timetable_id,
                TimetableModel.is_active.is_(True),
                TimetableModel.deleted_at.is_(None),
            )
            .options(selectinload(TimetableModel.entries))
        )
        result = await self.session.execute(stmt)
        timetable = result.scalar_one_or_none()
        if not timetable:
            raise NotFoundError("Timetable", str(timetable_id))
        return timetable

    async def publish(self, timetable_id: uuid.UUID) -> TimetableModel:
        timetable = await self.get_by_id(timetable_id)
        if timetable.status != TimetableStatus.GENERATED:
            raise BusinessRuleError(
                "Only generated timetables can be published"
            )
        return await self.update(timetable_id, status=TimetableStatus.PUBLISHED)

    async def archive(self, timetable_id: uuid.UUID) -> TimetableModel:
        return await self.update(timetable_id, status=TimetableStatus.ARCHIVED)

    async def clone(
        self, timetable_id: uuid.UUID, new_name: str
    ) -> TimetableModel:
        source = await self.get_with_entries(timetable_id)

        clone = await self.create(
            section_id=source.section_id,
            academic_calendar_id=source.academic_calendar_id,
            name=new_name,
            status=TimetableStatus.DRAFT,
            version=source.version + 1,
        )

        for entry in source.entries:
            te = TimetableEntryModel(
                timetable_id=clone.id,
                time_slot_id=entry.time_slot_id,
                section_id=entry.section_id,
                teacher_id=entry.teacher_id,
                subject_id=entry.subject_id,
                classroom_id=entry.classroom_id,
                laboratory_id=entry.laboratory_id,
                is_lab_session=entry.is_lab_session,
                notes=entry.notes,
            )
            self.session.add(te)

        await self.session.flush()
        return clone


class TimetableEntryService(BaseService):
    def __init__(self, session: AsyncSession):
        repo = BaseRepository(TimetableEntryModel, session)
        super().__init__(repo, session)
        self.session = session

    async def add_entry(
        self,
        timetable_id: uuid.UUID,
        time_slot_id: uuid.UUID,
        section_id: uuid.UUID,
        teacher_id: uuid.UUID,
        subject_id: uuid.UUID,
        classroom_id: uuid.UUID | None = None,
        laboratory_id: uuid.UUID | None = None,
        is_lab_session: bool = False,
        notes: str | None = None,
    ) -> TimetableEntryModel:
        return await self.create(
            timetable_id=timetable_id,
            time_slot_id=time_slot_id,
            section_id=section_id,
            teacher_id=teacher_id,
            subject_id=subject_id,
            classroom_id=classroom_id,
            laboratory_id=laboratory_id,
            is_lab_session=is_lab_session,
            notes=notes,
        )

    async def swap_entries(
        self, entry1_id: uuid.UUID, entry2_id: uuid.UUID
    ) -> tuple[TimetableEntryModel, TimetableEntryModel]:
        e1 = await self.get_by_id(entry1_id)
        e2 = await self.get_by_id(entry2_id)

        e1.time_slot_id, e2.time_slot_id = e2.time_slot_id, e1.time_slot_id
        await self.session.flush()
        return e1, e2


class ConflictService(BaseService):
    def __init__(self, session: AsyncSession):
        repo = BaseRepository(ConflictRecordModel, session)
        super().__init__(repo, session)
        self.session = session

    async def get_timetable_conflicts(
        self, timetable_id: uuid.UUID, resolved: bool | None = None
    ) -> list[ConflictRecordModel]:
        filters = {"timetable_id": timetable_id}
        if resolved is not None:
            filters["resolved"] = resolved
        items, _ = await self.repo.list(**filters)
        return items

    async def resolve_conflict(
        self, conflict_id: uuid.UUID, resolution: str, resolved_by: uuid.UUID
    ) -> ConflictRecordModel:
        return await self.update(
            conflict_id,
            resolved=True,
            resolution=resolution,
            resolved_by=resolved_by,
            resolved_at=datetime.now(timezone.utc),
        )

    async def detect_conflicts(
        self, timetable_id: uuid.UUID
    ) -> list[ConflictRecordModel]:
        stmt = (
            select(TimetableEntryModel)
            .where(
                TimetableEntryModel.timetable_id == timetable_id,
                TimetableEntryModel.is_active.is_(True),
            )
        )
        result = await self.session.execute(stmt)
        entries = list(result.scalars().all())

        conflicts = []

        for i, e1 in enumerate(entries):
            for e2 in entries[i + 1:]:
                if e1.time_slot_id != e2.time_slot_id:
                    continue

                if e1.teacher_id == e2.teacher_id:
                    conflicts.append(ConflictRecordModel(
                        timetable_id=timetable_id,
                        conflict_type=ConflictType.TEACHER_OVERLAP,
                        severity=ConflictSeverity.CRITICAL,
                        description=f"Teacher overlap at slot {e1.time_slot_id}",
                        involved_entries=[str(e1.id), str(e2.id)],
                    ))

                if e1.classroom_id and e2.classroom_id and e1.classroom_id == e2.classroom_id:
                    conflicts.append(ConflictRecordModel(
                        timetable_id=timetable_id,
                        conflict_type=ConflictType.ROOM_OVERLAP,
                        severity=ConflictSeverity.CRITICAL,
                        description=f"Room overlap at slot {e1.time_slot_id}",
                        involved_entries=[str(e1.id), str(e2.id)],
                    ))

                if e1.laboratory_id and e2.laboratory_id and e1.laboratory_id == e2.laboratory_id:
                    conflicts.append(ConflictRecordModel(
                        timetable_id=timetable_id,
                        conflict_type=ConflictType.LAB_OVERLAP,
                        severity=ConflictSeverity.CRITICAL,
                        description=f"Lab overlap at slot {e1.time_slot_id}",
                        involved_entries=[str(e1.id), str(e2.id)],
                    ))

        for c in conflicts:
            self.session.add(c)
        await self.session.flush()
        return conflicts
