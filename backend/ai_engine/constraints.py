import uuid
from collections import defaultdict

from ai_engine.models import CSPState, Teacher, TimeSlot, SlotType, HolidayInfo


def parse_minutes(t: str) -> int:
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def format_minutes(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


def slots_overlap(a: TimeSlot, b: TimeSlot) -> bool:
    if a.day_of_week != b.day_of_week:
        return False
    a_start = parse_minutes(a.start_time)
    a_end = parse_minutes(a.end_time)
    b_start = parse_minutes(b.start_time)
    b_end = parse_minutes(b.end_time)
    return a_start < b_end and b_start < a_end


def get_slot_minutes(slot: TimeSlot) -> int:
    return parse_minutes(slot.end_time) - parse_minutes(slot.start_time)


def is_slot_type_compatible(subject_type: str, slot_type: SlotType) -> bool:
    if subject_type in ("lab", "practical"):
        return slot_type in (SlotType.LAB, SlotType.LECTURE)
    if subject_type == "tutorial":
        return slot_type == SlotType.LECTURE
    return slot_type == SlotType.LECTURE


def check_teacher_available(teacher: Teacher, slot: TimeSlot) -> bool:
    for blocked in teacher.unavailable:
        if slot.day_of_week.lower() != blocked.day_of_week.lower():
            continue
        t_start = parse_minutes(slot.start_time)
        t_end = parse_minutes(slot.end_time)
        b_start = parse_minutes(blocked.start_time)
        b_end = parse_minutes(blocked.end_time)
        if t_start < b_end and b_start < t_end:
            return False
    return True


def is_holiday(slot: TimeSlot, holidays: list[HolidayInfo]) -> bool:
    for h in holidays:
        if h.day_of_week.lower() == slot.day_of_week.lower():
            return True
    return False


def is_break_slot(slot_id: uuid.UUID, break_ids: list[uuid.UUID]) -> bool:
    return slot_id in break_ids


def get_slot_key(slot_id: uuid.UUID, slot_map: dict[uuid.UUID, TimeSlot]) -> tuple:
    s = slot_map[slot_id]
    return (s.day_of_week, s.start_time, s.end_time)


def filter_domain_state(state: CSPState) -> dict[int, list[uuid.UUID]]:
    slot_map = state.slot_map
    working_day_ids = {
        s.id for s in state.time_slots
        if s.day_of_week.lower() in state.working_days
    }
    holiday_day_ids = set()
    for h in state.holidays:
        for s in state.time_slots:
            if s.day_of_week.lower() == h.day_of_week.lower():
                holiday_day_ids.add(s.id)

    break_id_set = set(state.break_slots)
    lunch_id_set = set(state.lunch_slots)

    domains: dict[int, list[uuid.UUID]] = {}
    for idx, assignment in enumerate(state.assignments):
        valid = []
        for slot in state.time_slots:
            if slot.id not in working_day_ids:
                continue
            if slot.id in holiday_day_ids:
                continue
            if slot.id in break_id_set:
                continue
            if slot.id in lunch_id_set:
                continue
            if not is_slot_type_compatible(assignment.subject.subject_type, slot.slot_type):
                continue
            teacher = state.teachers.get(assignment.teacher_id)
            if teacher and not check_teacher_available(teacher, slot):
                continue
            if assignment.subject.morning_only:
                slot_minutes = parse_minutes(slot.start_time)
                if slot_minutes >= 720:
                    continue
            if assignment.subject.afternoon_only:
                slot_minutes = parse_minutes(slot.start_time)
                if slot_minutes < 720:
                    continue
            if assignment.subject.is_fixed and assignment.subject.fixed_slot_ids:
                if slot.id not in assignment.subject.fixed_slot_ids:
                    continue
            valid.append(slot.id)
        domains[idx] = valid
    return domains


def check_hard_constraints(
    assignment_idx: int,
    slot_id: uuid.UUID,
    assignments_slots: dict[int, uuid.UUID],
    state: CSPState,
    room_assignments: dict[uuid.UUID, uuid.UUID] | None = None,
    lab_assignments: dict[uuid.UUID, uuid.UUID] | None = None,
) -> bool:
    slot_map = state.slot_map
    chosen = slot_map[slot_id]
    chosen_teacher = state.assignments[assignment_idx].teacher_id
    chosen_section = state.assignments[assignment_idx].section_id
    chosen_subject = state.assignments[assignment_idx].subject_id

    for other_idx, other_slot_id in assignments_slots.items():
        if other_slot_id is None or other_idx == assignment_idx:
            continue
        other_slot = slot_map[other_slot_id]
        if not slots_overlap(chosen, other_slot):
            continue
        other = state.assignments[other_idx]
        if other.teacher_id == chosen_teacher:
            return False
        if other.section_id == chosen_section:
            return False

    teacher = state.teachers.get(chosen_teacher)
    if teacher:
        day_count = 0
        for other_idx, other_slot_id in assignments_slots.items():
            if other_slot_id is None or other_idx == assignment_idx:
                continue
            other = state.assignments[other_idx]
            if other.teacher_id != chosen_teacher:
                continue
            oslot = slot_map[other_slot_id]
            if oslot.day_of_week == chosen.day_of_week:
                day_count += 1
        if day_count >= teacher.max_lectures_per_day:
            return False

        week_count = sum(1 for oi, osi in assignments_slots.items()
                         if osi is not None and oi != assignment_idx
                         and state.assignments[oi].teacher_id == chosen_teacher)
        if week_count >= teacher.max_lectures_per_week:
            return False

        consecutive = 1
        chosen_start = parse_minutes(chosen.start_time)
        for other_idx, other_slot_id in assignments_slots.items():
            if other_slot_id is None or other_idx == assignment_idx:
                continue
            other = state.assignments[other_idx]
            if other.teacher_id != chosen_teacher:
                continue
            oslot = slot_map[other_slot_id]
            if oslot.day_of_week != chosen.day_of_week:
                continue
            if parse_minutes(oslot.end_time) == chosen_start:
                consecutive += 1
        if consecutive > teacher.max_consecutive_lectures:
            return False

    if chosen_subject is not None:
        subject = state.subjects.get(chosen_subject)
        if subject and subject.morning_only and parse_minutes(chosen.start_time) >= 720:
            return False
        if subject and subject.afternoon_only and parse_minutes(chosen.start_time) < 720:
            return False

    return True


def count_soft_violations(state: CSPState, solution: dict[int, uuid.UUID]) -> int:
    violations = 0
    slot_map = state.slot_map

    teacher_day_slots: dict[uuid.UUID, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    section_day_slots: dict[uuid.UUID, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        assignment = state.assignments[idx]
        slot = slot_map[slot_id]
        teacher_day_slots[assignment.teacher_id][slot.day_of_week] += 1
        section_day_slots[assignment.section_id][slot.day_of_week] += 1

    for sc in state.soft_constraints:
        category = sc.get("category", "")
        priority = sc.get("priority", 5)
        config = sc.get("config", {})

        if category == "teacher_load":
            max_per_day = config.get("max_per_day", 6)
            for tid, days in teacher_day_slots.items():
                for day, count in days.items():
                    if count > max_per_day:
                        violations += priority * (count - max_per_day)

        elif category == "room_capacity":
            violations += priority

        elif category == "subject_spacing":
            for tid, days in teacher_day_slots.items():
                days_with_slots = sum(1 for c in days.values() if c > 0)
                if days_with_slots < 3:
                    violations += priority

        elif category == "preferred_time":
            for idx, slot_id in solution.items():
                if slot_id is None:
                    continue
                assignment = state.assignments[idx]
                teacher = state.teachers.get(assignment.teacher_id)
                if not teacher or not teacher.preferred_start_times:
                    continue
                slot = slot_map[slot_id]
                slot_start = parse_minutes(slot.start_time)
                has_preferred = any(
                    parse_minutes(t) <= slot_start <= parse_minutes(t) + 60
                    for t in teacher.preferred_start_times
                )
                if not has_preferred:
                    violations += priority

        elif category == "idle_periods":
            for idx, slot_id in solution.items():
                if slot_id is None:
                    continue
                assignment = state.assignments[idx]
                slot = slot_map[slot_id]
                day_slots = []
                for oi, osi in solution.items():
                    if osi is None or oi == idx:
                        continue
                    if state.assignments[oi].section_id != assignment.section_id:
                        continue
                    oslot = slot_map[osi]
                    if oslot.day_of_week == slot.day_of_week:
                        day_slots.append(parse_minutes(oslot.start_time))
                day_slots.sort()
                slot_start = parse_minutes(slot.start_time)
                for i in range(len(day_slots) - 1):
                    if day_slots[i] < slot_start < day_slots[i + 1]:
                        gap = day_slots[i + 1] - day_slots[i]
                        if gap > 90:
                            violations += priority
                            break

        elif category == "weekend_rule":
            for idx, slot_id in solution.items():
                if slot_id is None:
                    continue
                slot = slot_map[slot_id]
                if slot.day_of_week.lower() in ("saturday", "sunday"):
                    violations += priority

    return violations


def check_all_constraints(
    state: CSPState,
    solution: dict[int, uuid.UUID],
) -> dict[str, list[str]]:
    slot_map = state.slot_map
    results: dict[str, list[str]] = {
        "passed": [],
        "violated": [],
    }

    for sc in state.hard_constraints + state.soft_constraints:
        category = sc.get("category", "")
        config = sc.get("config", {})

        if category == "teacher_availability":
            violated = False
            for idx, slot_id in solution.items():
                if slot_id is None:
                    continue
                teacher = state.teachers.get(state.assignments[idx].teacher_id)
                slot = slot_map[slot_id]
                if teacher and not check_teacher_available(teacher, slot):
                    violated = True
                    results["violated"].append(
                        f"{teacher.full_name} unavailable at {slot.day_of_week} {slot.start_time}-{slot.end_time}"
                    )
            if not violated:
                results["passed"].append("All teachers available at assigned slots")

        elif category == "max_hours":
            max_weekly = config.get("max_weekly", 40)
            teacher_weekly: dict[uuid.UUID, int] = defaultdict(int)
            for idx, slot_id in solution.items():
                if slot_id is None:
                    continue
                tid = state.assignments[idx].teacher_id
                slot = slot_map[slot_id]
                teacher_weekly[tid] += get_slot_minutes(slot)
            for tid, total in teacher_weekly.items():
                if total > max_weekly * 60:
                    teacher = state.teachers.get(tid)
                    results["violated"].append(
                        f"{teacher.full_name if teacher else 'Unknown'} exceeds {max_weekly}h/week"
                    )

        elif category == "min_hours":
            min_weekly = config.get("min_weekly", 10)
            teacher_weekly = defaultdict(int)
            for idx, slot_id in solution.items():
                if slot_id is None:
                    continue
                tid = state.assignments[idx].teacher_id
                slot = slot_map[slot_id]
                teacher_weekly[tid] += get_slot_minutes(slot)
            for tid, total in teacher_weekly.items():
                if total < min_weekly * 60:
                    teacher = state.teachers.get(tid)
                    results["violated"].append(
                        f"{teacher.full_name if teacher else 'Unknown'} below {min_weekly}h/week minimum"
                    )

        elif category == "lab_requirement":
            for idx, slot_id in solution.items():
                if slot_id is None:
                    continue
                assignment = state.assignments[idx]
                if assignment.is_lab:
                    slot = slot_map[slot_id]
                    slot_dur = get_slot_minutes(slot)
                    required = assignment.lab_duration or 60
                    if slot_dur < required:
                        results["violated"].append(
                            f"Lab {assignment.subject.name} requires {required}min slot, got {slot_dur}min"
                        )

        elif category == "department_restriction":
            for idx, slot_id in solution.items():
                if slot_id is None:
                    continue
                assignment = state.assignments[idx]
                teacher = state.teachers.get(assignment.teacher_id)
                subject = state.subjects.get(assignment.subject_id)
                if teacher and subject and teacher.department_id and subject.department_id:
                    if teacher.department_id != subject.department_id and not teacher.is_shared:
                        results["violated"].append(
                            f"Teacher from dept {teacher.department_id} assigned to subject from dept {subject.department_id}"
                        )

        elif category == "semester_restriction":
            for idx, slot_id in solution.items():
                if slot_id is None:
                    continue
                slot = slot_map[slot_id]
                if slot.day_of_week.lower() not in state.working_days:
                    results["violated"].append(
                        f"Assignment {idx} on non-working day {slot.day_of_week}"
                    )

        elif category == "holiday_rule":
            for idx, slot_id in solution.items():
                if slot_id is None:
                    continue
                slot = slot_map[slot_id]
                if is_holiday(slot, state.holidays):
                    results["violated"].append(
                        f"Assignment {idx} on holiday ({slot.day_of_week})"
                    )

    if not results["violated"]:
        results["passed"].append("All constraints satisfied")

    return results
