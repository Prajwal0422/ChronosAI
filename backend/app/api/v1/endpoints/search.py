import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.deps import get_db_session, get_current_user_role
from app.infrastructure.database.models import (
    TeacherModel, SubjectModel, ClassroomModel, LaboratoryModel,
    TimetableModel, TimetableEntryModel, SectionModel, DepartmentModel,
)

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("")
async def global_search(
    q: str = Query("", min_length=1),
    entity_type: str | None = Query(None),
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(get_current_user_role),
):
    if not q:
        return {"query": "", "results": [], "total": 0}

    results: list[dict] = []
    search_term = f"%{q}%"

    if not entity_type or entity_type == "teachers":
        teacher_query = select(TeacherModel).where(
            TeacherModel.is_active.is_(True),
            TeacherModel.deleted_at.is_(None),
            or_(
                TeacherModel.full_name.ilike(search_term),
                TeacherModel.employee_code.ilike(search_term),
                TeacherModel.email.ilike(search_term),
            ),
        ).limit(limit)
        teachers = (await session.execute(teacher_query)).scalars().all()
        for t in teachers:
            results.append({
                "type": "teacher",
                "id": str(t.id),
                "label": t.full_name,
                "subtitle": f"{t.employee_code} · {t.email}",
                "url": f"/teachers?id={t.id}",
            })

    if not entity_type or entity_type == "subjects":
        subject_query = select(SubjectModel).where(
            SubjectModel.is_active.is_(True),
            SubjectModel.deleted_at.is_(None),
            or_(
                SubjectModel.name.ilike(search_term),
                SubjectModel.code.ilike(search_term),
            ),
        ).limit(limit)
        subjects = (await session.execute(subject_query)).scalars().all()
        for s in subjects:
            results.append({
                "type": "subject",
                "id": str(s.id),
                "label": s.name,
                "subtitle": f"{s.code} · {s.subject_type}",
                "url": f"/subjects?id={s.id}",
            })

    if not entity_type or entity_type == "classrooms":
        room_query = select(ClassroomModel).where(
            ClassroomModel.is_active.is_(True),
            ClassroomModel.deleted_at.is_(None),
            or_(
                ClassroomModel.name.ilike(search_term),
                ClassroomModel.code.ilike(search_term),
                ClassroomModel.building.ilike(search_term),
            ),
        ).limit(limit)
        rooms = (await session.execute(room_query)).scalars().all()
        for r in rooms:
            results.append({
                "type": "classroom",
                "id": str(r.id),
                "label": r.name,
                "subtitle": f"{r.code} · Capacity: {r.capacity}",
                "url": f"/classrooms?id={r.id}",
            })

    if not entity_type or entity_type == "laboratories":
        lab_query = select(LaboratoryModel).where(
            LaboratoryModel.is_active.is_(True),
            LaboratoryModel.deleted_at.is_(None),
            or_(
                LaboratoryModel.name.ilike(search_term),
                LaboratoryModel.code.ilike(search_term),
            ),
        ).limit(limit)
        labs = (await session.execute(lab_query)).scalars().all()
        for l in labs:
            results.append({
                "type": "laboratory",
                "id": str(l.id),
                "label": l.name,
                "subtitle": f"{l.code} · Capacity: {l.capacity}",
                "url": f"/laboratories?id={l.id}",
            })

    if not entity_type or entity_type == "timetables":
        tt_query = select(TimetableModel).where(
            TimetableModel.is_active.is_(True),
            TimetableModel.deleted_at.is_(None),
            TimetableModel.name.ilike(search_term),
        ).limit(limit)
        tts = (await session.execute(tt_query)).scalars().all()
        for tt in tts:
            section_name = ""
            if tt.section_id:
                section = await session.get(SectionModel, tt.section_id)
                if section:
                    section_name = section.name
            results.append({
                "type": "timetable",
                "id": str(tt.id),
                "label": tt.name,
                "subtitle": f"Section: {section_name} · v{tt.version} · Score: {tt.quality_score or 'N/A'}",
                "url": f"/timetables?id={tt.id}",
            })

    return {
        "query": q,
        "results": results,
        "total": len(results),
    }


@router.get("/suggestions")
async def search_suggestions(
    q: str = Query("", min_length=1),
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(get_current_user_role),
):
    if not q:
        return {"suggestions": []}
    search_term = f"%{q}%"
    suggestions: list[str] = []

    teacher_result = await session.execute(
        select(TeacherModel.full_name).where(
            TeacherModel.full_name.ilike(search_term),
            TeacherModel.is_active.is_(True),
        ).limit(3)
    )
    suggestions.extend(row[0] for row in teacher_result)

    subject_result = await session.execute(
        select(SubjectModel.name).where(
            SubjectModel.name.ilike(search_term),
            SubjectModel.is_active.is_(True),
        ).limit(3)
    )
    suggestions.extend(row[0] for row in subject_result)

    return {"suggestions": suggestions[:8]}
