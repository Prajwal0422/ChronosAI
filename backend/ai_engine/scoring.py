import uuid
from collections import defaultdict
from dataclasses import dataclass

from ai_engine.models import CSPState
from ai_engine.constraints import parse_minutes


@dataclass
class ScoreComponents:
    base_score: float = 0.0
    weekly_distribution: float = 0.0
    load_balance: float = 0.0
    compactness: float = 0.0
    gap_penalty: float = 0.0
    resource_utilization: float = 0.0
    preferred_slots: float = 0.0
    idle_periods: float = 0.0
    room_switching: float = 0.0
    faculty_switching: float = 0.0
    student_experience: float = 0.0
    constraint_satisfaction: float = 0.0

    def total(self) -> float:
        return max(0.0, min(100.0, sum([
            self.base_score,
            self.weekly_distribution * 12.0,
            self.load_balance * 10.0,
            self.compactness * 8.0,
            self.resource_utilization * 8.0,
            self.preferred_slots * 8.0,
            self.student_experience * 6.0,
            self.constraint_satisfaction * 10.0,
        ]) - (self.gap_penalty * 5.0 + self.idle_periods * 4.0 + self.room_switching * 3.0 + self.faculty_switching * 3.0)))


def score_solution(state: CSPState, solution: dict[int, uuid.UUID]) -> float:
    if not solution:
        return 0.0

    assigned = sum(1 for v in solution.values() if v is not None)
    total = len(state.assignments)
    if total == 0:
        return 100.0

    slot_map = state.slot_map
    teachers = state.teachers

    components = _compute_all_components(state, solution, slot_map, teachers)
    return round(components.total(), 2)


def compute_detailed_score(state: CSPState, solution: dict[int, uuid.UUID]) -> ScoreComponents:
    slot_map = state.slot_map
    teachers = state.teachers
    return _compute_all_components(state, solution, slot_map, teachers)


def _compute_all_components(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict,
    teachers: dict,
) -> ScoreComponents:
    c = ScoreComponents()
    c.base_score = 50.0
    c.weekly_distribution = _score_weekly_distribution(state, solution, slot_map)
    c.load_balance = _score_load_balance(state, solution, slot_map, teachers)
    c.compactness = _score_compactness(state, solution, slot_map)
    c.gap_penalty = _score_gaps(state, solution, slot_map)
    c.resource_utilization = _score_resource_utilization(state, solution)
    c.preferred_slots = _score_preferred_slots(state, solution, slot_map, teachers)
    c.idle_periods = _score_idle_periods(state, solution, slot_map)
    c.room_switching = _score_room_switching(state, solution, slot_map)
    c.faculty_switching = _score_faculty_switching(state, solution, slot_map)
    c.student_experience = _score_student_experience(
        state, solution, slot_map, c.compactness, c.gap_penalty, c.weekly_distribution
    )
    c.constraint_satisfaction = _score_constraint_satisfaction(state, solution)
    return c


def _score_weekly_distribution(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict,
) -> float:
    section_days: dict[uuid.UUID, set[str]] = defaultdict(set)
    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        assignment = state.assignments[idx]
        slot = slot_map[slot_id]
        section_days[assignment.section_id].add(slot.day_of_week)

    if not section_days:
        return 0.0

    avg_days = sum(len(days) for days in section_days.values()) / len(section_days)
    return min(1.0, avg_days / 5.0)


def _score_load_balance(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict,
    teachers: dict,
) -> float:
    teacher_counts: dict[uuid.UUID, int] = defaultdict(int)
    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        tid = state.assignments[idx].teacher_id
        teacher_counts[tid] += 1

    if not teacher_counts:
        return 0.0

    counts = list(teacher_counts.values())
    avg = sum(counts) / len(counts)
    variance = sum((c - avg) ** 2 for c in counts) / len(counts)
    max_variance = (avg * len(counts)) ** 2 / max(1, len(counts))
    if max_variance == 0:
        return 1.0
    return max(0.0, 1.0 - (variance / max_variance))


def _score_compactness(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict,
) -> float:
    section_day_slots: dict = defaultdict(list)
    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        assignment = state.assignments[idx]
        slot = slot_map[slot_id]
        section_day_slots[(assignment.section_id, slot.day_of_week)].append(
            parse_minutes(slot.start_time)
        )

    if not section_day_slots:
        return 0.0

    total_span = 0
    count = 0
    for key, times in section_day_slots.items():
        if len(times) <= 1:
            continue
        times.sort()
        span = times[-1] - times[0]
        total_span += span
        count += 1

    if count == 0:
        return 1.0

    avg_span = total_span / count
    ideal_span = 240
    ratio = max(0.0, 1.0 - (avg_span / max(ideal_span, 1)))
    return ratio


def _score_gaps(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict,
) -> float:
    section_day_sorted: dict = defaultdict(list)
    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        assignment = state.assignments[idx]
        slot = slot_map[slot_id]
        section_day_sorted[(assignment.section_id, slot.day_of_week)].append(
            parse_minutes(slot.start_time)
        )

    total_gaps = 0
    for key, times in section_day_sorted.items():
        times.sort()
        for i in range(len(times) - 1):
            gap = times[i + 1] - times[i]
            if gap > 60:
                total_gaps += gap - 60

    max_possible_gaps = 600 * len(section_day_sorted)
    if max_possible_gaps == 0:
        return 0.0
    return min(1.0, total_gaps / max_possible_gaps)


def _score_resource_utilization(
    state: CSPState,
    solution: dict[int, uuid.UUID],
) -> float:
    if not state.classrooms and not state.laboratories:
        return 0.5

    assigned = sum(1 for v in solution.values() if v is not None)
    total = len(state.assignments)
    if total == 0:
        return 1.0
    return assigned / total


def _score_preferred_slots(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict,
    teachers: dict,
) -> float:
    total_preferred = 0
    total_slots = 0

    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        total_slots += 1
        assignment = state.assignments[idx]
        teacher = teachers.get(assignment.teacher_id)
        if not teacher or not teacher.preferred_start_times:
            total_preferred += 1
            continue
        slot = slot_map[slot_id]
        slot_start = parse_minutes(slot.start_time)
        is_preferred = any(
            parse_minutes(t) <= slot_start <= parse_minutes(t) + 60
            for t in teacher.preferred_start_times
        )
        if is_preferred:
            total_preferred += 1

    if total_slots == 0:
        return 0.0
    return total_preferred / total_slots


def _score_idle_periods(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict,
) -> float:
    section_day_sorted: dict = defaultdict(list)
    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        assignment = state.assignments[idx]
        slot = slot_map[slot_id]
        section_day_sorted[(assignment.section_id, slot.day_of_week)].append(
            parse_minutes(slot.start_time)
        )

    total_idle = 0
    for key, times in section_day_sorted.items():
        times.sort()
        for i in range(len(times) - 1):
            gap = times[i + 1] - times[i]
            if gap > 90:
                total_idle += gap - 90

    if not section_day_sorted:
        return 0.0
    max_idle = 300 * len(section_day_sorted)
    return min(1.0, total_idle / max(max_idle, 1))


def _score_room_switching(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict,
) -> float:
    section_day_slots: dict = defaultdict(list)
    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        assignment = state.assignments[idx]
        slot = slot_map[slot_id]
        section_day_slots[(assignment.section_id, slot.day_of_week)].append(
            parse_minutes(slot.start_time)
        )

    if not section_day_slots:
        return 0.0
    total_days = len(section_day_slots)
    days_with_multiple = sum(1 for times in section_day_slots.values() if len(times) > 1)
    ratio = days_with_multiple / total_days if total_days > 0 else 0
    return ratio


def _score_faculty_switching(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict,
) -> float:
    section_day_teachers: dict = defaultdict(set)
    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        assignment = state.assignments[idx]
        slot = slot_map[slot_id]
        section_day_teachers[(assignment.section_id, slot.day_of_week)].add(
            assignment.teacher_id
        )

    if not section_day_teachers:
        return 0.0
    total_days = len(section_day_teachers)
    days_with_multiple = sum(1 for teachers in section_day_teachers.values() if len(teachers) > 1)
    ratio = days_with_multiple / total_days if total_days > 0 else 0
    return 1.0 - ratio


def _score_student_experience(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict,
    compactness: float,
    gap_penalty: float,
    distribution: float,
) -> float:
    return (compactness * 0.4 + (1.0 - gap_penalty) * 0.3 + distribution * 0.3)


def _score_constraint_satisfaction(
    state: CSPState,
    solution: dict[int, uuid.UUID],
) -> float:
    total_constraints = len(state.hard_constraints) + len(state.soft_constraints)
    if total_constraints == 0:
        return 1.0

    from ai_engine.constraints import count_soft_violations
    violations = count_soft_violations(state, solution)

    max_possible = total_constraints * 10
    satisfied = max(0, max_possible - violations)
    return satisfied / max(max_possible, 1)
