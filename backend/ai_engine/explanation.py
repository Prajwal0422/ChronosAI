import uuid
from collections import defaultdict

from ai_engine.models import (
    CSPState, GenerationReport, ConflictInfo, RepairAction,
    ValidationResult, Recommendation,
)
from ai_engine.scoring import score_solution, compute_detailed_score


def generate_report(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    conflicts: list[ConflictInfo],
    repairs: list[RepairAction],
    validation: ValidationResult,
    recommendations: list[Recommendation],
    generation_time: float,
    solutions_generated: int,
    solution_selected: str,
) -> GenerationReport:
    score = score_solution(state, solution)
    detailed = compute_detailed_score(state, solution)

    resource_utilization = _compute_resource_utilization(state, solution)
    faculty_load = _compute_faculty_load(state, solution)
    room_utilization = _compute_room_utilization(state, solution)
    constraint_satisfaction_pct = _compute_constraint_pct(
        state, solution, validation, conflicts
    )

    reasoning_parts: list[str] = []
    reasoning_parts.append(f"Generated {solutions_generated} candidate solution(s), selected via {solution_selected} strategy.")
    reasoning_parts.append(f"Overall quality score: {score}/100.")

    if detailed:
        reasoning_parts.append(
            f"Score breakdown: base={detailed.base_score:.1f}, "
            f"distribution={detailed.weekly_distribution:.2f}, "
            f"load_balance={detailed.load_balance:.2f}, "
            f"compactness={detailed.compactness:.2f}, "
            f"gap_penalty={detailed.gap_penalty:.2f}, "
            f"resource_util={detailed.resource_utilization:.2f}, "
            f"preferred_slots={detailed.preferred_slots:.2f}, "
            f"idle={detailed.idle_periods:.2f}, "
            f"student_exp={detailed.student_experience:.2f}, "
            f"constraint_satisfaction={detailed.constraint_satisfaction:.2f}."
        )

    reasoning_parts.append(f"Constraint satisfaction: {constraint_satisfaction_pct:.1f}%.")
    reasoning_parts.append(f"Validation: {'PASSED' if validation.is_valid else 'FAILED'} ({validation.coverage_pct}% coverage).")

    if conflicts:
        critical_count = sum(1 for c in conflicts if c.severity.value == "critical")
        high_count = sum(1 for c in conflicts if c.severity.value == "high")
        medium_count = sum(1 for c in conflicts if c.severity.value == "medium")
        reasoning_parts.append(
            f"Conflicts detected: {len(conflicts)} total "
            f"({critical_count} critical, {high_count} high, {medium_count} medium)."
        )

    if repairs:
        reasoning_parts.append(f"Applied {len(repairs)} auto-repair(s) to resolve conflicts.")
        repair_types = defaultdict(int)
        for r in repairs:
            repair_types[r.action_type] += 1
        for rtype, count in repair_types.items():
            reasoning_parts.append(f"  - {rtype}: {count}")
    else:
        reasoning_parts.append("No repairs needed.")

    if recommendations:
        reason_high = sum(1 for r in recommendations if r.priority == "high")
        reason_medium = sum(1 for r in recommendations if r.priority == "medium")
        reasoning_parts.append(
            f"Recommendations: {len(recommendations)} "
            f"({reason_high} high, {reason_medium} medium priority)."
        )

    reasoning_summary = " | ".join(reasoning_parts)

    return GenerationReport(
        score=round(score, 2),
        constraint_satisfaction_pct=round(constraint_satisfaction_pct, 1),
        optimization_score=detailed.total() if detailed else score,
        detected_conflicts=conflicts,
        repairs_applied=repairs,
        generation_time_seconds=round(generation_time, 3),
        resource_utilization=resource_utilization,
        faculty_load=faculty_load,
        room_utilization=room_utilization,
        reasoning_summary=reasoning_summary,
        solutions_generated=solutions_generated,
        solution_selected=solution_selected,
    )


def _compute_resource_utilization(
    state: CSPState,
    solution: dict[int, uuid.UUID],
) -> dict[str, float]:
    total = len(state.assignments)
    if total == 0:
        return {"overall": 1.0}
    assigned = sum(1 for v in solution.values() if v is not None)
    return {"overall": round(assigned / total, 3)}


def _compute_faculty_load(
    state: CSPState,
    solution: dict[int, uuid.UUID],
) -> dict[str, int]:
    load: dict[str, int] = {}
    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        teacher = state.teachers.get(state.assignments[idx].teacher_id)
        name = teacher.full_name if teacher else str(state.assignments[idx].teacher_id)
        load[name] = load.get(name, 0) + 1
    return load


def _compute_room_utilization(
    state: CSPState,
    solution: dict[int, uuid.UUID],
) -> dict[str, float]:
    room_usage: dict[str, int] = {}
    for cr in state.classrooms:
        room_usage[str(cr.id)] = 0
    for lab in state.laboratories:
        room_usage[str(lab.id)] = 0

    if not room_usage:
        return {}

    assigned_count = sum(1 for v in solution.values() if v is not None)
    if assigned_count == 0:
        return {k: 0.0 for k in room_usage}

    per_room = max(1, assigned_count // len(room_usage))
    return {
        rid: round(min(1.0, count / per_room), 3) if per_room > 0 else 0.0
        for rid, count in room_usage.items()
    }


def _compute_constraint_pct(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    validation: ValidationResult,
    conflicts: list[ConflictInfo],
) -> float:
    total_constraints = len(state.hard_constraints) + len(state.soft_constraints)
    if total_constraints == 0:
        return 100.0

    violated_count = len(validation.errors) + len(validation.warnings) + len(conflicts)
    satisfied = max(0, total_constraints - violated_count)
    return (satisfied / total_constraints) * 100.0
