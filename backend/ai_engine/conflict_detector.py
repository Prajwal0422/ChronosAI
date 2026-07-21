import uuid
from collections import defaultdict

from ai_engine.models import (
    CSPState, TimeSlot, ConflictInfo, ConflictSeverity,
    SlotType,
)
from ai_engine.constraints import (
    parse_minutes, slots_overlap, check_teacher_available,
    is_holiday, is_break_slot,
)


def detect_all_conflicts(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    room_map: dict[uuid.UUID, uuid.UUID] | None = None,
    lab_map: dict[uuid.UUID, uuid.UUID] | None = None,
) -> list[ConflictInfo]:
    conflicts: list[ConflictInfo] = []
    slot_map = state.slot_map

    conflicts.extend(_detect_teacher_double_booking(state, solution, slot_map))
    conflicts.extend(_detect_room_double_booking(state, solution, slot_map, room_map))
    conflicts.extend(_detect_lab_conflicts(state, solution, slot_map, lab_map))
    conflicts.extend(_detect_holiday_conflicts(state, solution, slot_map))
    conflicts.extend(_detect_lunch_break_conflicts(state, solution, slot_map))
    conflicts.extend(_detect_working_hour_violations(state, solution, slot_map))
    conflicts.extend(_detect_teacher_leave_conflicts(state, solution, slot_map))
    conflicts.extend(_detect_subject_distribution_conflicts(state, solution, slot_map))

    return conflicts


def _detect_teacher_double_booking(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict[uuid.UUID, TimeSlot],
) -> list[ConflictInfo]:
    conflicts: list[ConflictInfo] = []
    teacher_slot_map: dict[uuid.UUID, dict[uuid.UUID, list[int]]] = defaultdict(lambda: defaultdict(list))

    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        tid = state.assignments[idx].teacher_id
        teacher_slot_map[tid][slot_id].append(idx)

    for tid, slot_indices in teacher_slot_map.items():
        slot_ids = list(slot_indices.keys())
        for i in range(len(slot_ids)):
            for j in range(i + 1, len(slot_ids)):
                si = slot_map[slot_ids[i]]
                sj = slot_map[slot_ids[j]]
                if slots_overlap(si, sj):
                    teacher = state.teachers.get(tid)
                    indices = list(set(slot_indices[slot_ids[i]] + slot_indices[slot_ids[j]]))
                    conflicts.append(ConflictInfo(
                        conflict_type="teacher_double_booking",
                        severity=ConflictSeverity.CRITICAL,
                        description=f"Teacher '{teacher.full_name if teacher else str(tid)}' double-booked at {si.day_of_week} {si.start_time}-{si.end_time} and {sj.day_of_week} {sj.start_time}-{sj.end_time}",
                        involved_slots=[slot_ids[i], slot_ids[j]],
                        involved_teachers=[tid],
                        involved_sections=list(set(
                            state.assignments[idx].section_id for idx in indices
                        )),
                        details={
                            "teacher_id": str(tid),
                            "slots": [str(s) for s in [slot_ids[i], slot_ids[j]]],
                            "assignments": indices,
                        },
                    ))

    return conflicts


def _detect_room_double_booking(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict[uuid.UUID, TimeSlot],
    room_map: dict[uuid.UUID, uuid.UUID] | None,
) -> list[ConflictInfo]:
    conflicts: list[ConflictInfo] = []
    if not room_map:
        return conflicts

    room_slot_map: dict[uuid.UUID, dict[uuid.UUID, list[int]]] = defaultdict(lambda: defaultdict(list))
    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        rid = room_map.get(slot_id)
        if rid:
            room_slot_map[rid][slot_id].append(idx)

    for rid, slot_indices in room_slot_map.items():
        slot_ids = list(slot_indices.keys())
        for i in range(len(slot_ids)):
            for j in range(i + 1, len(slot_ids)):
                si = slot_map[slot_ids[i]]
                sj = slot_map[slot_ids[j]]
                if slots_overlap(si, sj):
                    conflicts.append(ConflictInfo(
                        conflict_type="room_double_booking",
                        severity=ConflictSeverity.CRITICAL,
                        description=f"Room {rid} double-booked at overlapping time slots",
                        involved_slots=[slot_ids[i], slot_ids[j]],
                        involved_rooms=[rid],
                        details={
                            "room_id": str(rid),
                            "slots": [str(s) for s in [slot_ids[i], slot_ids[j]]],
                        },
                    ))

    return conflicts


def _detect_lab_conflicts(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict[uuid.UUID, TimeSlot],
    lab_map: dict[uuid.UUID, uuid.UUID] | None,
) -> list[ConflictInfo]:
    conflicts: list[ConflictInfo] = []
    if not lab_map:
        return conflicts

    lab_slot_map: dict[uuid.UUID, dict[uuid.UUID, list[int]]] = defaultdict(lambda: defaultdict(list))
    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        lid = lab_map.get(slot_id)
        if lid:
            lab_slot_map[lid][slot_id].append(idx)

    for lid, slot_indices in lab_slot_map.items():
        slot_ids = list(slot_indices.keys())
        for i in range(len(slot_ids)):
            for j in range(i + 1, len(slot_ids)):
                si = slot_map[slot_ids[i]]
                sj = slot_map[slot_ids[j]]
                if slots_overlap(si, sj):
                    conflicts.append(ConflictInfo(
                        conflict_type="laboratory_conflict",
                        severity=ConflictSeverity.CRITICAL,
                        description=f"Laboratory {lid} double-booked at overlapping time slots",
                        involved_slots=[slot_ids[i], slot_ids[j]],
                        involved_rooms=[lid],
                        details={
                            "lab_id": str(lid),
                            "slots": [str(s) for s in [slot_ids[i], slot_ids[j]]],
                        },
                    ))

    return conflicts


def _detect_holiday_conflicts(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict[uuid.UUID, TimeSlot],
) -> list[ConflictInfo]:
    conflicts: list[ConflictInfo] = []
    if not state.holidays:
        return conflicts

    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        slot = slot_map[slot_id]
        if is_holiday(slot, state.holidays):
            holiday_name = next(
                (h.name for h in state.holidays if h.day_of_week.lower() == slot.day_of_week.lower()),
                "Unknown",
            )
            conflicts.append(ConflictInfo(
                conflict_type="holiday_conflict",
                severity=ConflictSeverity.HIGH,
                description=f"Class scheduled on holiday '{holiday_name}' ({slot.day_of_week})",
                involved_slots=[slot_id],
                details={
                    "holiday": holiday_name,
                    "day": slot.day_of_week,
                    "assignment_idx": idx,
                },
            ))

    return conflicts


def _detect_lunch_break_conflicts(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict[uuid.UUID, TimeSlot],
) -> list[ConflictInfo]:
    conflicts: list[ConflictInfo] = []
    break_ids = set(state.break_slots)
    lunch_ids = set(state.lunch_slots)

    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        if slot_id in break_ids:
            conflicts.append(ConflictInfo(
                conflict_type="lunch_conflict",
                severity=ConflictSeverity.HIGH,
                description=f"Class scheduled during break period",
                involved_slots=[slot_id],
                details={"assignment_idx": idx, "slot_id": str(slot_id)},
            ))
        if slot_id in lunch_ids:
            conflicts.append(ConflictInfo(
                conflict_type="lunch_conflict",
                severity=ConflictSeverity.HIGH,
                description=f"Class scheduled during lunch period",
                involved_slots=[slot_id],
                details={"assignment_idx": idx, "slot_id": str(slot_id)},
            ))

    return conflicts


def _detect_working_hour_violations(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict[uuid.UUID, TimeSlot],
) -> list[ConflictInfo]:
    conflicts: list[ConflictInfo] = []
    working_day_set = {d.lower() for d in state.working_days}

    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        slot = slot_map[slot_id]
        if slot.day_of_week.lower() not in working_day_set:
            conflicts.append(ConflictInfo(
                conflict_type="working_hour_violation",
                severity=ConflictSeverity.HIGH,
                description=f"Class scheduled on non-working day {slot.day_of_week}",
                involved_slots=[slot_id],
                details={"assignment_idx": idx, "day": slot.day_of_week},
            ))

    return conflicts


def _detect_teacher_leave_conflicts(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict[uuid.UUID, TimeSlot],
) -> list[ConflictInfo]:
    conflicts: list[ConflictInfo] = []
    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        assignment = state.assignments[idx]
        teacher = state.teachers.get(assignment.teacher_id)
        slot = slot_map[slot_id]
        if teacher and not check_teacher_available(teacher, slot):
            conflicts.append(ConflictInfo(
                conflict_type="faculty_leave_conflict",
                severity=ConflictSeverity.HIGH,
                description=f"Teacher '{teacher.full_name}' on leave at {slot.day_of_week} {slot.start_time}-{slot.end_time}",
                involved_slots=[slot_id],
                involved_teachers=[assignment.teacher_id],
                details={
                    "teacher_id": str(assignment.teacher_id),
                    "slot_id": str(slot_id),
                    "assignment_idx": idx,
                },
            ))

    return conflicts


def _detect_subject_distribution_conflicts(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict[uuid.UUID, TimeSlot],
) -> list[ConflictInfo]:
    conflicts: list[ConflictInfo] = []
    subject_day_slots: dict[uuid.UUID, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        assignment = state.assignments[idx]
        slot = slot_map[slot_id]
        subject_day_slots[assignment.subject_id][slot.day_of_week] += 1

    for subj_id, days in subject_day_slots.items():
        total_slots = sum(days.values())
        days_used = len(days)
        if total_slots >= 3 and days_used < 2:
            subject = state.subjects.get(subj_id)
            conflicts.append(ConflictInfo(
                conflict_type="subject_distribution_violation",
                severity=ConflictSeverity.MEDIUM,
                description=f"Subject '{subject.name if subject else subj_id}' ({total_slots}hrs) concentrated on {days_used} day(s)",
                involved_slots=[],
                details={
                    "subject_id": str(subj_id),
                    "total_slots": total_slots,
                    "days_used": days_used,
                },
            ))

    return conflicts


def detect_conflicts_between_entries(
    section_slots: dict[uuid.UUID, list[tuple[uuid.UUID, uuid.UUID, uuid.UUID, uuid.UUID, uuid.UUID]]],
    time_slots: dict[uuid.UUID, TimeSlot],
) -> list[ConflictInfo]:
    conflicts: list[ConflictInfo] = []
    teacher_slot_map: dict[uuid.UUID, dict[uuid.UUID, list]] = defaultdict(lambda: defaultdict(list))
    room_slot_map: dict = defaultdict(lambda: defaultdict(list))

    for section_id, entries in section_slots.items():
        for time_slot_id, teacher_id, subject_id, classroom_id, lab_id in entries:
            teacher_slot_map[teacher_id][time_slot_id].append((section_id, subject_id))
            if classroom_id:
                room_slot_map[f"room:{classroom_id}"][time_slot_id].append(section_id)
            if lab_id:
                room_slot_map[f"lab:{lab_id}"][time_slot_id].append(section_id)

    for tid, slot_entries in teacher_slot_map.items():
        slot_ids = list(slot_entries.keys())
        for i in range(len(slot_ids)):
            for j in range(i + 1, len(slot_ids)):
                si = time_slots.get(slot_ids[i])
                sj = time_slots.get(slot_ids[j])
                if si and sj and slots_overlap(si, sj):
                    conflicts.append(ConflictInfo(
                        conflict_type="teacher_double_booking",
                        severity=ConflictSeverity.CRITICAL,
                        description=f"Teacher {tid} double-booked at overlapping slots",
                        involved_slots=[slot_ids[i], slot_ids[j]],
                        involved_teachers=[tid],
                    ))

    for resource_key, slot_entries in room_slot_map.items():
        slot_ids = list(slot_entries.keys())
        for i in range(len(slot_ids)):
            for j in range(i + 1, len(slot_ids)):
                si = time_slots.get(slot_ids[i])
                sj = time_slots.get(slot_ids[j])
                if si and sj and slots_overlap(si, sj):
                    resource_type, resource_id = resource_key.split(":", 1)
                    conflicts.append(ConflictInfo(
                        conflict_type="room_double_booking" if resource_type == "room" else "laboratory_conflict",
                        severity=ConflictSeverity.CRITICAL,
                        description=f"{resource_type.title()} {resource_id} double-booked",
                        involved_slots=[slot_ids[i], slot_ids[j]],
                        involved_rooms=[uuid.UUID(resource_id)] if resource_id else [],
                    ))

    return conflicts
