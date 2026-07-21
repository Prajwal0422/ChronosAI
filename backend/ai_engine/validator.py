import uuid

from ai_engine.models import CSPState, ValidationResult
from ai_engine.constraints import (
    check_hard_constraints, check_teacher_available, parse_minutes, get_slot_minutes,
)


def validate_solution(state: CSPState, solution: dict[int, uuid.UUID]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    slot_map = state.slot_map

    for idx, slot_id in solution.items():
        if slot_id is None:
            assignment = state.assignments[idx]
            errors.append(f"Assignment #{idx} ({assignment.subject.name}) has no time slot assigned")
            continue

        if slot_id not in slot_map:
            errors.append(f"Assignment #{idx} references invalid time slot {slot_id}")
            continue

    if errors:
        return ValidationResult(is_valid=False, errors=errors, coverage_pct=_calculate_coverage(solution, len(state.assignments)))

    assigned_slots: dict[int, uuid.UUID] = {}
    for idx, slot_id in solution.items():
        if slot_id is not None:
            assigned_slots[idx] = slot_id

    for idx, slot_id in assigned_slots.items():
        if not check_hard_constraints(idx, slot_id, assigned_slots, state):
            assignment = state.assignments[idx]
            errors.append(
                f"Hard constraint violated: Assignment #{idx} ({assignment.subject.name}) at slot {slot_id}"
            )

    for idx, slot_id in assigned_slots.items():
        teacher = state.teachers.get(state.assignments[idx].teacher_id)
        slot = slot_map[slot_id]
        if teacher and not check_teacher_available(teacher, slot):
            assignment = state.assignments[idx]
            warnings.append(
                f"Teacher '{teacher.full_name}' unavailable at {slot.day_of_week} {slot.start_time} for {assignment.subject.name}"
            )

    section_slots: dict[uuid.UUID, list[uuid.UUID]] = {}
    for idx, slot_id in assigned_slots.items():
        sid = state.assignments[idx].section_id
        section_slots.setdefault(sid, []).append(slot_id)

    for sid, slots in section_slots.items():
        if len(slots) != len(set(slots)):
            warnings.append(f"Section {sid} has duplicate time slot assignments")

    working_minutes: dict[uuid.UUID, int] = {}
    for idx, slot_id in assigned_slots.items():
        tid = state.assignments[idx].teacher_id
        slot = slot_map[slot_id]
        working_minutes[tid] = working_minutes.get(tid, 0) + get_slot_minutes(slot)

    for tid, minutes in working_minutes.items():
        teacher = state.teachers.get(tid)
        if teacher and minutes > teacher.max_lectures_per_week * 60:
            warnings.append(
                f"Teacher '{teacher.full_name}' exceeds max weekly hours ({minutes // 60}h > {teacher.max_lectures_per_week}h)"
            )

    coverage_pct = _calculate_coverage(solution, len(state.assignments))
    is_valid = len(errors) == 0

    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        coverage_pct=coverage_pct,
    )


def _calculate_coverage(solution: dict[int, uuid.UUID], total_assignments: int) -> float:
    if total_assignments == 0:
        return 100.0
    assigned = sum(1 for v in solution.values() if v is not None)
    return round((assigned / total_assignments) * 100, 1)
