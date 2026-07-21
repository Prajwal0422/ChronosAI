import uuid
from copy import deepcopy
from collections import defaultdict

from ai_engine.models import CSPState, RepairAction, ConflictInfo, ConflictSeverity
from ai_engine.constraints import (
    check_hard_constraints, filter_domain_state, slots_overlap,
    check_teacher_available, parse_minutes,
)
from ai_engine.scoring import score_solution


def auto_repair(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    conflicts: list[ConflictInfo],
    max_iterations: int = 10,
) -> tuple[dict[int, uuid.UUID], list[RepairAction]]:
    repairs: list[RepairAction] = []
    current = dict(solution)
    slot_map = state.slot_map
    domains = filter_domain_state(state)

    for iteration in range(max_iterations):
        critical_conflicts = [c for c in conflicts if c.severity in (ConflictSeverity.CRITICAL, ConflictSeverity.HIGH)]
        if not critical_conflicts:
            break

        repairs_found = False
        for conflict in critical_conflicts:
            repair_actions = _analyze_conflict(state, current, conflict, domains, slot_map)
            for action in repair_actions:
                idx = action.assignment_idx
                old_id = current.get(idx)
                new_id = action.new_slot_id

                if new_id is not None and old_id != new_id:
                    temp = dict(current)
                    temp[idx] = new_id
                    assigned = {i: sid for i, sid in temp.items() if sid is not None}
                    slot_valid = True
                    for other_idx in assigned:
                        if other_idx == idx:
                            continue
                        if slots_overlap(slot_map[assigned[other_idx]], slot_map[assigned[idx]]):
                            other = state.assignments[other_idx]
                            if other.teacher_id == state.assignments[idx].teacher_id:
                                slot_valid = False
                                break
                            if other.section_id == state.assignments[idx].section_id:
                                slot_valid = False
                                break
                    if slot_valid:
                        current[idx] = new_id
                        repairs.append(action)
                        repairs_found = True
                        break

        if not repairs_found:
            for conflict in critical_conflicts:
                repair_actions = _analyze_conflict(state, current, conflict, domains, slot_map)
                for action in repair_actions:
                    idx = action.assignment_idx
                    new_id = action.new_slot_id
                    if new_id is not None:
                        current[idx] = new_id
                        repairs.append(action)
                        repairs_found = True
                        break

        if not repairs_found:
            break

    return current, repairs


def _analyze_conflict(
    state: CSPState,
    current: dict[int, uuid.UUID],
    conflict: ConflictInfo,
    domains: dict[int, list[uuid.UUID]],
    slot_map: dict[uuid.UUID, uuid.UUID | None],
) -> list[RepairAction]:
    actions: list[RepairAction] = []
    slot_map_ts = {s.id: s for s in state.time_slots}
    detail_assignments = conflict.details.get("assignments", [])

    if conflict.conflict_type == "teacher_double_booking":
        for idx_str in detail_assignments:
            idx = int(idx_str) if isinstance(idx_str, (int, str)) else idx_str
            if isinstance(idx, str):
                try:
                    idx = int(idx)
                except ValueError:
                    continue
            current_slot = current.get(idx)
            if current_slot is None:
                continue
            domain = domains.get(idx, [])
            alternatives = _find_alternatives(
                state, current, idx, domain, slot_map_ts, conflict.involved_slots
            )
            for alt_id, reason in alternatives[:3]:
                actions.append(RepairAction(
                    action_type="reschedule",
                    description=f"Move {state.assignments[idx].subject.name} to alternative time slot",
                    assignment_idx=idx,
                    old_slot_id=current_slot,
                    new_slot_id=alt_id,
                    reason=reason,
                ))

    elif conflict.conflict_type == "room_double_booking":
        _add_room_alternatives(actions, state, current, conflict, domains, slot_map_ts)

    elif conflict.conflict_type in ("holiday_conflict", "lunch_conflict", "working_hour_violation"):
        for idx in detail_assignments:
            if isinstance(idx, str):
                try:
                    idx = int(idx)
                except ValueError:
                    continue
            current_slot = current.get(idx)
            if current_slot is None:
                continue
            domain = domains.get(idx, [])
            alternatives = _find_alternatives_any(state, current, idx, domain, slot_map_ts)
            for alt_id, reason in alternatives[:3]:
                actions.append(RepairAction(
                    action_type="reschedule",
                    description=f"Move {state.assignments[idx].subject.name} out of {conflict.conflict_type.replace('_', ' ')}",
                    assignment_idx=idx,
                    old_slot_id=current_slot,
                    new_slot_id=alt_id,
                    reason=reason,
                ))

    elif conflict.conflict_type == "faculty_leave_conflict":
        teacher_id_str = conflict.details.get("teacher_id", "")
        if teacher_id_str:
            for idx, slot_id in current.items():
                if slot_id is None:
                    continue
                if state.assignments[idx].teacher_id == uuid.UUID(teacher_id_str):
                    domain = domains.get(idx, [])
                    alternatives = _find_alternatives_any(state, current, idx, domain, slot_map_ts)
                    for alt_id, reason in alternatives[:2]:
                        actions.append(RepairAction(
                            action_type="reschedule",
                            description=f"Move {state.assignments[idx].subject.name} due to teacher leave",
                            assignment_idx=idx,
                            old_slot_id=slot_id,
                            new_slot_id=alt_id,
                            reason=reason,
                        ))

    return actions


def _find_alternatives(
    state: CSPState,
    current: dict[int, uuid.UUID],
    idx: int,
    domain: list[uuid.UUID],
    slot_map: dict[uuid.UUID, uuid.UUID],
    exclude_slots: list[uuid.UUID],
) -> list[tuple[uuid.UUID, str]]:
    alternatives: list[tuple[uuid.UUID, str]] = []
    for slot_id in domain:
        if slot_id in exclude_slots:
            continue
        temp = dict(current)
        temp[idx] = slot_id
        assigned = {i: sid for i, sid in temp.items() if sid is not None}
        if check_hard_constraints(idx, slot_id, assigned, state):
            slot = slot_map.get(slot_id)
            if slot:
                name = getattr(slot, 'day_of_week', '') + ' ' + getattr(slot, 'start_time', '')
                alternatives.append((slot_id, f"Available at {name}"))
            else:
                alternatives.append((slot_id, "Available alternative slot"))
    return alternatives


def _find_alternatives_any(
    state: CSPState,
    current: dict[int, uuid.UUID],
    idx: int,
    domain: list[uuid.UUID],
    slot_map: dict[uuid.UUID, uuid.UUID],
) -> list[tuple[uuid.UUID, str]]:
    return _find_alternatives(state, current, idx, domain, slot_map, [])


def _add_room_alternatives(
    actions: list[RepairAction],
    state: CSPState,
    current: dict[int, uuid.UUID],
    conflict: ConflictInfo,
    domains: dict[int, list[uuid.UUID]],
    slot_map: dict[uuid.UUID, uuid.UUID],
):
    for idx, slot_id in current.items():
        if slot_id is None:
            continue
        if str(slot_id) in [str(s) for s in conflict.involved_slots]:
            domain = domains.get(idx, [])
            alternatives = _find_alternatives_any(state, current, idx, domain, slot_map)
            for alt_id, reason in alternatives[:2]:
                actions.append(RepairAction(
                    action_type="reassign_room",
                    description=f"Reassign room for {state.assignments[idx].subject.name}",
                    assignment_idx=idx,
                    old_slot_id=slot_id,
                    new_slot_id=alt_id,
                    reason=reason,
                ))


def explain_repairs(repairs: list[RepairAction]) -> str:
    if not repairs:
        return "No repairs were needed. The schedule is conflict-free."

    lines = [f"Applied {len(repairs)} repair(s):"]
    for i, r in enumerate(repairs, 1):
        old = f" from {r.old_slot_id}" if r.old_slot_id else ""
        new = f" to {r.new_slot_id}" if r.new_slot_id else ""
        lines.append(f"  {i}. {r.description}{old}{new}")
        if r.reason:
            lines.append(f"     Reason: {r.reason}")
    return "\n".join(lines)
