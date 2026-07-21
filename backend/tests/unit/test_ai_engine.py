import uuid
import pytest

from ai_engine.models import (
    CSPState, TeachingAssignment, TimeSlot, Teacher, Subject,
    Classroom, Laboratory, Section, TimeRange, SlotType,
)
from ai_engine.constraints import (
    check_hard_constraints, filter_domain_state, slots_overlap,
    is_slot_type_compatible, check_teacher_available, parse_minutes,
    count_soft_violations,
)
from ai_engine.scoring import score_solution


@pytest.fixture
def sample_slot_ids():
    return [uuid.uuid4() for _ in range(6)]


@pytest.fixture
def sample_time_slots(sample_slot_ids):
    return [
        TimeSlot(id=sample_slot_ids[0], day_of_week="monday", start_time="08:00", end_time="09:00", slot_type=SlotType.LECTURE),
        TimeSlot(id=sample_slot_ids[1], day_of_week="monday", start_time="09:00", end_time="10:00", slot_type=SlotType.LECTURE),
        TimeSlot(id=sample_slot_ids[2], day_of_week="monday", start_time="10:00", end_time="11:00", slot_type=SlotType.LECTURE),
        TimeSlot(id=sample_slot_ids[3], day_of_week="tuesday", start_time="08:00", end_time="09:00", slot_type=SlotType.LECTURE),
        TimeSlot(id=sample_slot_ids[4], day_of_week="tuesday", start_time="09:00", end_time="10:00", slot_type=SlotType.LECTURE),
        TimeSlot(id=sample_slot_ids[5], day_of_week="tuesday", start_time="14:00", end_time="16:00", slot_type=SlotType.LAB),
    ]


@pytest.fixture
def sample_teachers():
    t1_id = uuid.uuid4()
    t2_id = uuid.uuid4()
    return {
        t1_id: Teacher(id=t1_id, full_name="Dr. Smith", max_lectures_per_day=4, max_lectures_per_week=20, max_consecutive_lectures=3, is_shared=False),
        t2_id: Teacher(id=t2_id, full_name="Prof. Jones", max_lectures_per_day=3, max_lectures_per_week=15, max_consecutive_lectures=2, is_shared=False),
    }


@pytest.fixture
def sample_subjects():
    s1_id = uuid.uuid4()
    s2_id = uuid.uuid4()
    return {
        s1_id: Subject(id=s1_id, name="Mathematics", code="MTH101", subject_type="theory", lectures_per_week=3, is_elective=False, is_lab=False),
        s2_id: Subject(id=s2_id, name="Physics Lab", code="PHY101", subject_type="lab", lectures_per_week=2, is_elective=False, is_lab=True, lab_duration=2),
    }


@pytest.fixture
def sample_state(sample_time_slots, sample_teachers, sample_subjects):
    section_id = uuid.uuid4()
    teacher_ids = list(sample_teachers.keys())
    subject_ids = list(sample_subjects.keys())

    assignments = [
        TeachingAssignment(
            section_id=section_id,
            subject_id=subject_ids[0],
            teacher_id=teacher_ids[0],
            subject=sample_subjects[subject_ids[0]],
            lectures_per_week=3,
            is_lab=False,
        ),
        TeachingAssignment(
            section_id=section_id,
            subject_id=subject_ids[1],
            teacher_id=teacher_ids[1],
            subject=sample_subjects[subject_ids[1]],
            lectures_per_week=2,
            is_lab=True,
            lab_duration=2,
        ),
    ]

    return CSPState(
        timetable_id=uuid.uuid4(),
        section_id=section_id,
        assignments=assignments,
        time_slots=sample_time_slots,
        teachers=sample_teachers,
        subjects=sample_subjects,
        classrooms=[Classroom(id=uuid.uuid4(), capacity=60, room_type="lecture")],
        laboratories=[Laboratory(id=uuid.uuid4(), capacity=30)],
        working_days={"monday", "tuesday"},
        hard_constraints=[],
        soft_constraints=[],
    )


class TestSlotsOverlap:
    def test_overlapping_slots(self):
        s1 = TimeSlot(id=uuid.uuid4(), day_of_week="monday", start_time="08:00", end_time="10:00", slot_type=SlotType.LECTURE)
        s2 = TimeSlot(id=uuid.uuid4(), day_of_week="monday", start_time="09:00", end_time="11:00", slot_type=SlotType.LECTURE)
        assert slots_overlap(s1, s2)

    def test_non_overlapping_slots(self, sample_time_slots):
        assert not slots_overlap(sample_time_slots[0], sample_time_slots[4])
        assert not slots_overlap(sample_time_slots[0], sample_time_slots[3])

    def test_different_days_no_overlap(self, sample_time_slots):
        assert not slots_overlap(sample_time_slots[0], sample_time_slots[3])


class TestSlotTypeCompatibility:
    def test_theory_in_lecture_slot(self):
        assert is_slot_type_compatible("theory", SlotType.LECTURE)
        assert not is_slot_type_compatible("theory", SlotType.LAB)

    def test_lab_in_any_compatible_slot(self):
        assert is_slot_type_compatible("lab", SlotType.LAB)
        assert is_slot_type_compatible("lab", SlotType.LECTURE)

    def test_tutorial_in_lecture_only(self):
        assert is_slot_type_compatible("tutorial", SlotType.LECTURE)
        assert not is_slot_type_compatible("tutorial", SlotType.BREAK)
        assert not is_slot_type_compatible("tutorial", SlotType.LUNCH)


class TestCheckTeacherAvailable:
    def test_teacher_available_no_unavailable(self, sample_teachers):
        tid = list(sample_teachers.keys())[0]
        teacher = sample_teachers[tid]
        slot = TimeSlot(id=uuid.uuid4(), day_of_week="monday", start_time="08:00", end_time="09:00", slot_type=SlotType.LECTURE)
        assert check_teacher_available(teacher, slot)

    def test_teacher_unavailable(self, sample_teachers):
        tid = list(sample_teachers.keys())[0]
        teacher = sample_teachers[tid]
        teacher.unavailable = [TimeRange(day_of_week="monday", start_time="08:00", end_time="10:00")]
        slot = TimeSlot(id=uuid.uuid4(), day_of_week="monday", start_time="09:00", end_time="10:00", slot_type=SlotType.LECTURE)
        assert not check_teacher_available(teacher, slot)


class TestHardConstraints:
    def test_no_conflict_on_first_assignment(self, sample_state):
        assigned = {}
        result = check_hard_constraints(0, sample_state.time_slots[0].id, assigned, sample_state)
        assert result

    def test_teacher_overlap_rejected(self, sample_state):
        slot_id = sample_state.time_slots[0].id
        assigned = {0: slot_id}
        result = check_hard_constraints(1, slot_id, assigned, sample_state)
        assert not result

    def test_different_slot_accepted(self, sample_state):
        assigned = {0: sample_state.time_slots[0].id}
        result = check_hard_constraints(1, sample_state.time_slots[1].id, assigned, sample_state)
        assert result

    def test_same_teacher_multiple_classes(self, sample_state):
        t_id = list(sample_state.teachers.keys())[0]
        section_id = uuid.uuid4()
        subj_id = list(sample_state.subjects.keys())[0]
        third_assignment = TeachingAssignment(
            section_id=section_id,
            subject_id=subj_id,
            teacher_id=t_id,
            subject=sample_state.subjects[subj_id],
            lectures_per_week=1,
            is_lab=False,
        )
        sample_state.assignments.append(third_assignment)

        assigned = {0: sample_state.time_slots[0].id}
        # Same teacher at same slot as assignment 0 (which has same teacher)
        result = check_hard_constraints(2, sample_state.time_slots[0].id, assigned, sample_state)
        assert not result


class TestFilterDomainState:
    def test_returns_domains_for_all_assignments(self, sample_state):
        domains = filter_domain_state(sample_state)
        assert len(domains) == len(sample_state.assignments)
        for idx in domains:
            assert len(domains[idx]) > 0

    def test_domains_have_working_days_only(self, sample_state):
        domains = filter_domain_state(sample_state)
        day_of_week_slot = {s.id: s.day_of_week for s in sample_state.time_slots}
        for idx, slot_ids in domains.items():
            for sid in slot_ids:
                assert day_of_week_slot[sid] in sample_state.working_days

    def test_lab_assignment_gets_lab_slots(self, sample_state):
        domains = filter_domain_state(sample_state)
        lab_assignment_idx = 1
        assert len(domains[lab_assignment_idx]) > 0


class TestScoreSolution:
    def test_empty_solution_scores_zero(self, sample_state):
        score = score_solution(sample_state, {})
        assert score == 0.0

    def test_complete_solution_scores_above_zero(self, sample_state):
        solution = {
            0: sample_state.time_slots[0].id,
            1: sample_state.time_slots[4].id,
        }
        score = score_solution(sample_state, solution)
        assert score > 0
        assert score <= 100

    def test_better_distribution_scores_higher(self, sample_state):
        solution_good = {
            0: sample_state.time_slots[0].id,
            1: sample_state.time_slots[4].id,
        }
        solution_bad = {
            0: sample_state.time_slots[0].id,
            1: sample_state.time_slots[1].id,
        }
        score_good = score_solution(sample_state, solution_good)
        score_bad = score_solution(sample_state, solution_bad)
        assert score_good >= score_bad


class TestParseMinutes:
    def test_parse_minutes(self):
        assert parse_minutes("08:00") == 480
        assert parse_minutes("00:00") == 0
        assert parse_minutes("23:59") == 1439


class TestCountSoftViolations:
    def test_no_violations_no_soft_constraints(self, sample_state):
        solution = {0: sample_state.time_slots[0].id, 1: sample_state.time_slots[4].id}
        violations = count_soft_violations(sample_state, solution)
        assert violations == 0


class TestBacktrackingSolver:
    def test_backtrack_produces_solutions(self, sample_state):
        from ai_engine.solver import TimetableSolver
        from ai_engine.constraints import filter_domain_state

        solver = TimetableSolver.__new__(TimetableSolver)
        domains = filter_domain_state(sample_state)
        solutions = solver._backtrack(sample_state, domains)

        assert isinstance(solutions, list)
        assert len(solutions) > 0
        for sol in solutions:
            assert len(sol) == len(sample_state.assignments)
            for idx, slot_id in sol.items():
                assert slot_id is not None

    def test_backtrack_respects_hard_constraints(self, sample_state):
        from ai_engine.solver import TimetableSolver
        from ai_engine.constraints import filter_domain_state

        solver = TimetableSolver.__new__(TimetableSolver)
        domains = filter_domain_state(sample_state)
        solutions = solver._backtrack(sample_state, domains)

        for sol in solutions:
            assigned = {}
            for idx, slot_id in sol.items():
                assert check_hard_constraints(idx, slot_id, assigned, sample_state)
                assigned[idx] = slot_id

    def test_solution_to_entries(self, sample_state):
        from ai_engine.solver import TimetableSolver
        from ai_engine.constraints import filter_domain_state

        solver = TimetableSolver.__new__(TimetableSolver)
        domains = filter_domain_state(sample_state)
        solutions = solver._backtrack(sample_state, domains)

        if solutions:
            entries = solver._solution_to_entries(
                uuid.uuid4(), sample_state.section_id, solutions[0], sample_state
            )
            assert len(entries) == len(sample_state.assignments)
            for e in entries:
                assert "time_slot_id" in e
                assert "teacher_id" in e
                assert "subject_id" in e
                assert "section_id" in e
