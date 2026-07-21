import uuid
import time
import asyncio
from functools import partial

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_engine.models import (
    CSPState,
    TeachingAssignment,
    TimeSlot,
    Teacher,
    Subject,
    Classroom,
    Laboratory,
    Section,
    TimeRange,
    SlotType,
    GenerationReport,
    HolidayInfo,
)
from ai_engine.constraints import (
    check_hard_constraints,
    filter_domain_state,
)
from ai_engine.scoring import score_solution
from ai_engine.genetic import genetic_refine, _assign_rooms_labs
from ai_engine.conflict_detector import detect_all_conflicts
from ai_engine.validator import validate_solution
from ai_engine.repair import auto_repair
from ai_engine.recommender import generate_recommendations
from ai_engine.explanation import generate_report

from app.infrastructure.database.models import (
    TimetableModel,
    TimeSlotModel,
    TeacherModel,
    TeacherUnavailableModel,
    SubjectModel,
    SubjectAssignmentModel,
    ClassroomModel,
    LaboratoryModel,
    SectionModel,
    ConstraintModel,
    WorkingDayModel,
    HolidayModel,
)
from app.core.constants import ConstraintType


MAX_SOLUTIONS = 3
MAX_BACKTRACKS = 50000
USE_GENETIC_REFINEMENT = True


class TimetableSolver:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def solve(
        self,
        timetable: TimetableModel,
        constraints: list[ConstraintModel],
    ) -> dict:
        start_time = time.time()
        state = await self._build_state(timetable, constraints)
        if not state.assignments:
            return {
                "entries": [],
                "score": 100.0,
                "solutions_generated": 0,
                "solution_selected": "none",
                "report": generate_report(
                    state, {}, [], [], validate_solution(state, {}), [],
                    0.0, 0, "none",
                ).__dict__,
            }

        loop = asyncio.get_event_loop()
        cpu_result = await loop.run_in_executor(
            None, partial(self._solve_cpu_bound, state)
        )

        generation_time = time.time() - start_time
        cpu_result["generation_time"] = generation_time
        cpu_result["report"]["generation_time_seconds"] = generation_time
        cpu_result["report"]["elapsed"] = generation_time

        entries = self._solution_to_entries(
            timetable.id, timetable.section_id, cpu_result["best_solution"], state,
            cpu_result["room_assignments"], cpu_result["lab_assignments"],
        )

        return {
            "entries": entries,
            "score": round(cpu_result["best_score"], 2),
            "solutions_generated": cpu_result["solutions_count"],
            "solution_selected": cpu_result["solution_selected"],
            "report": cpu_result["report"],
        }

    def _solve_cpu_bound(self, state: CSPState) -> dict:
        domains = filter_domain_state(state)
        solutions = self._backtrack(state, domains)

        if not solutions:
            empty_report = generate_report(
                state, {}, [], [], validate_solution(state, {}),
                [], 0.0, 0, "none",
            )
            return {
                "best_solution": {},
                "best_score": 0.0,
                "solutions_count": 0,
                "solution_selected": "none",
                "room_assignments": {},
                "lab_assignments": {},
                "report": empty_report.__dict__,
            }

        scored = [(score_solution(state, sol), sol) for sol in solutions]
        scored.sort(key=lambda x: x[0], reverse=True)

        best_score, best_solution = scored[0]
        solution_selected = "backtrack"

        if USE_GENETIC_REFINEMENT and best_score < 100.0:
            refined = genetic_refine(state, best_solution)
            refined_score = score_solution(state, refined)
            if refined_score > best_score:
                best_score = refined_score
                best_solution = refined
                solution_selected = "genetic"

        room_assignments, lab_assignments = _assign_rooms_labs(state, best_solution)
        conflicts = detect_all_conflicts(state, best_solution, room_assignments, lab_assignments)
        repaired_solution, repairs = auto_repair(state, best_solution, conflicts)

        if repairs:
            best_solution = repaired_solution
            room_assignments, lab_assignments = _assign_rooms_labs(state, best_solution)
            best_score = score_solution(state, best_solution)
            conflicts = detect_all_conflicts(state, best_solution, room_assignments, lab_assignments)

        validation = validate_solution(state, best_solution)
        recommendations = generate_recommendations(state, best_solution, best_score, validation.coverage_pct)

        report = generate_report(
            state, best_solution, conflicts, repairs, validation,
            recommendations, 0.0, len(solutions), solution_selected,
        )

        return {
            "best_solution": best_solution,
            "best_score": best_score,
            "solutions_count": len(solutions),
            "solution_selected": solution_selected,
            "room_assignments": room_assignments,
            "lab_assignments": lab_assignments,
            "report": report.__dict__,
        }

    async def _build_state(
        self,
        timetable: TimetableModel,
        constraints: list[ConstraintModel],
    ) -> CSPState:
        section_result = await self.session.execute(
            select(SectionModel).where(
                SectionModel.id == timetable.section_id,
                SectionModel.is_active.is_(True),
                SectionModel.deleted_at.is_(None),
            )
        )
        section_model = section_result.scalar_one_or_none()
        section = Section(
            id=section_model.id, name=section_model.name, strength=section_model.strength
        ) if section_model else Section(id=timetable.section_id, name="", strength=0)

        time_slot_models = (
            await self.session.execute(
                select(TimeSlotModel).where(
                    TimeSlotModel.is_active.is_(True),
                    TimeSlotModel.deleted_at.is_(None),
                )
            )
        ).scalars().all()
        time_slots = [
            TimeSlot(
                id=ts.id,
                day_of_week=ts.day_of_week,
                start_time=ts.start_time,
                end_time=ts.end_time,
                slot_type=SlotType(ts.slot_type) if isinstance(ts.slot_type, str) else ts.slot_type,
                slot_group=ts.slot_group,
            )
            for ts in time_slot_models
        ]

        teacher_models = (
            await self.session.execute(
                select(TeacherModel).where(
                    TeacherModel.is_active.is_(True),
                    TeacherModel.deleted_at.is_(None),
                )
            )
        ).scalars().all()

        teacher_ids = [t.id for t in teacher_models]
        unavail_models_all = []
        if teacher_ids:
            unavail_result = await self.session.execute(
                select(TeacherUnavailableModel).where(
                    TeacherUnavailableModel.teacher_id.in_(teacher_ids),
                )
            )
            unavail_models_all = unavail_result.scalars().all()

        unavail_by_teacher: dict[uuid.UUID, list[TimeRange]] = {}
        for u in unavail_models_all:
            if u.teacher_id not in unavail_by_teacher:
                unavail_by_teacher[u.teacher_id] = []
            unavail_by_teacher[u.teacher_id].append(
                TimeRange(day_of_week=u.day_of_week, start_time=u.start_time, end_time=u.end_time)
            )

        teachers: dict[uuid.UUID, Teacher] = {}
        for t in teacher_models:
            unavail = unavail_by_teacher.get(t.id, [])
            teachers[t.id] = Teacher(
                id=t.id,
                full_name=t.full_name,
                max_lectures_per_day=t.max_lectures_per_day,
                max_lectures_per_week=t.max_lectures_per_week,
                max_consecutive_lectures=t.max_consecutive_lectures,
                is_shared=t.is_shared,
                unavailable=unavail,
            )

        subject_models = (
            await self.session.execute(
                select(SubjectModel).where(
                    SubjectModel.is_active.is_(True),
                    SubjectModel.deleted_at.is_(None),
                )
            )
        ).scalars().all()
        subjects: dict[uuid.UUID, Subject] = {
            s.id: Subject(
                id=s.id,
                name=s.name,
                code=s.code,
                subject_type=s.subject_type,
                lectures_per_week=s.lectures_per_week,
                is_elective=s.is_elective,
                is_lab=s.is_lab,
                lab_duration=s.lab_duration,
            )
            for s in subject_models
        }

        classroom_models = (
            await self.session.execute(
                select(ClassroomModel).where(
                    ClassroomModel.is_active.is_(True),
                    ClassroomModel.deleted_at.is_(None),
                )
            )
        ).scalars().all()
        classrooms = [
            Classroom(id=c.id, capacity=c.capacity, room_type=c.room_type)
            for c in classroom_models
        ]

        lab_models = (
            await self.session.execute(
                select(LaboratoryModel).where(
                    LaboratoryModel.is_active.is_(True),
                    LaboratoryModel.deleted_at.is_(None),
                )
            )
        ).scalars().all()
        laboratories = [
            Laboratory(id=l.id, capacity=l.capacity) for l in lab_models
        ]

        assignment_models = (
            await self.session.execute(
                select(SubjectAssignmentModel).where(
                    SubjectAssignmentModel.section_id == timetable.section_id,
                    SubjectAssignmentModel.is_active.is_(True),
                    SubjectAssignmentModel.deleted_at.is_(None),
                )
            )
        ).scalars().all()

        assignments: list[TeachingAssignment] = []
        for a in assignment_models:
            subj = subjects.get(a.subject_id)
            if not subj:
                continue
            assignments.append(
                TeachingAssignment(
                    section_id=a.section_id,
                    subject_id=a.subject_id,
                    teacher_id=a.teacher_id,
                    subject=subj,
                    lectures_per_week=subj.lectures_per_week,
                    is_lab=subj.is_lab,
                    lab_duration=subj.lab_duration,
                )
            )

        working_day_models = (
            await self.session.execute(select(WorkingDayModel))
        ).scalars().all()
        working_days = {wd.day_of_week.lower() for wd in working_day_models}
        if not working_days:
            working_days = {"monday", "tuesday", "wednesday", "thursday", "friday"}

        holiday_models = (
            await self.session.execute(select(HolidayModel))
        ).scalars().all()
        holidays = [
            HolidayInfo(
                date=str(h.holiday_date),
                day_of_week=h.holiday_date.strftime("%A").lower(),
                name=h.name,
                is_public=getattr(h, "is_public", True),
            )
            for h in holiday_models
        ]

        hard_constraints = [c for c in constraints if c.constraint_type == ConstraintType.HARD]
        soft_constraints = [c for c in constraints if c.constraint_type == ConstraintType.SOFT]

        return CSPState(
            timetable_id=timetable.id,
            section_id=timetable.section_id,
            assignments=assignments,
            time_slots=time_slots,
            teachers=teachers,
            subjects=subjects,
            classrooms=classrooms,
            laboratories=laboratories,
            working_days=working_days,
            holidays=holidays,
            slot_map={ts.id: ts for ts in time_slots},
            hard_constraints=[
                {"id": str(c.id), "category": c.category, "config": c.config, "priority": c.priority}
                for c in hard_constraints
            ],
            soft_constraints=[
                {"id": str(c.id), "category": c.category, "config": c.config, "priority": c.priority}
                for c in soft_constraints
            ],
        )

    def _backtrack(
        self,
        state: CSPState,
        domains: dict[int, list[uuid.UUID]],
    ) -> list[dict[int, uuid.UUID]]:
        solutions: list[dict[int, uuid.UUID]] = []
        assignment_count = len(state.assignments)
        self._backtrack_count = 0

        def _select_unassigned(assigned: dict[int, uuid.UUID]):
            best_idx = -1
            best_domain_size = float("inf")
            for idx in range(assignment_count):
                if idx in assigned:
                    continue
                domain = domains.get(idx, [])
                remaining = [s for s in domain if s not in {assigned.get(i) for i in assigned}]
                if len(remaining) < best_domain_size:
                    best_domain_size = len(remaining)
                    best_idx = idx
            return best_idx

        def _order_values(idx: int, assigned: dict[int, uuid.UUID]):
            return domains.get(idx, [])

        def _search(assigned: dict[int, uuid.UUID]):
            if self._backtrack_count > MAX_BACKTRACKS:
                return
            if len(assigned) == assignment_count:
                sol = dict(assigned)
                if sol not in solutions:
                    solutions.append(sol)
                return

            self._backtrack_count += 1
            idx = _select_unassigned(assigned)
            if idx < 0:
                return

            for slot_id in _order_values(idx, assigned):
                if not check_hard_constraints(idx, slot_id, assigned, state):
                    continue
                assigned[idx] = slot_id
                _search(assigned)
                del assigned[idx]
                if len(solutions) >= MAX_SOLUTIONS:
                    return

        _search({})
        return solutions

    def _solution_to_entries(
        self,
        timetable_id: uuid.UUID,
        section_id: uuid.UUID,
        solution: dict[int, uuid.UUID],
        state: CSPState,
        room_assignments: dict[uuid.UUID, uuid.UUID | None] | None = None,
        lab_assignments: dict[uuid.UUID, uuid.UUID | None] | None = None,
    ) -> list[dict]:
        entries: list[dict] = []
        slot_map = state.slot_map
        room_map = room_assignments or {}
        lab_map = lab_assignments or {}
        classroom_pool = list(state.classrooms)
        lab_pool = list(state.laboratories)
        used_classrooms: dict[uuid.UUID, set[uuid.UUID]] = {}
        used_labs: dict[uuid.UUID, set[uuid.UUID]] = {}

        for idx, slot_id in solution.items():
            if slot_id is None:
                continue
            assignment = state.assignments[idx]

            classroom_id = room_map.get(slot_id)
            laboratory_id = lab_map.get(slot_id)

            if classroom_id is None and laboratory_id is None:
                if assignment.is_lab:
                    for lab in lab_pool:
                        booked = used_labs.setdefault(slot_id, set())
                        if lab.id not in booked:
                            laboratory_id = lab.id
                            booked.add(lab.id)
                            break
                else:
                    for cr in classroom_pool:
                        booked = used_classrooms.setdefault(slot_id, set())
                        if cr.id not in booked:
                            classroom_id = cr.id
                            booked.add(cr.id)
                            break

            entries.append({
                "timetable_id": timetable_id,
                "time_slot_id": slot_id,
                "section_id": section_id,
                "teacher_id": assignment.teacher_id,
                "subject_id": assignment.subject_id,
                "classroom_id": classroom_id,
                "laboratory_id": laboratory_id,
                "is_lab_session": assignment.is_lab,
            })

        return entries
