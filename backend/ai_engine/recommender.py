import uuid
from collections import defaultdict

from ai_engine.models import CSPState, Recommendation
from ai_engine.constraints import parse_minutes


def generate_recommendations(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    score: float,
    coverage_pct: float,
) -> list[Recommendation]:
    recommendations: list[Recommendation] = []
    slot_map = state.slot_map

    recommendations.extend(_recommend_coverage(coverage_pct, len(state.assignments)))
    recommendations.extend(_recommend_score_improvement(score))
    recommendations.extend(_recommend_load_balancing(state, solution, slot_map))
    recommendations.extend(_recommend_distribution(state, solution, slot_map))
    recommendations.extend(_recommend_idle_time(state, solution, slot_map))
    recommendations.extend(_recommend_teacher_availability(state))
    recommendations.extend(_recommend_resource_usage(state, score))

    return recommendations


def _recommend_coverage(coverage_pct: float, total: int) -> list[Recommendation]:
    if coverage_pct < 100.0:
        return [Recommendation(
            category="coverage",
            priority="high",
            description=f"Only {coverage_pct}% of assignments are scheduled ({total - int(total * coverage_pct / 100)} unscheduled)",
            impact="Incomplete timetable leaves gaps in student schedules",
            suggested_action="Add more time slots or reduce subject assignments per section",
        )]
    return []


def _recommend_score_improvement(score: float) -> list[Recommendation]:
    if score < 60:
        return [Recommendation(
            category="quality",
            priority="high",
            description=f"Overall quality score ({score}/100) is below acceptable threshold",
            impact="Poor quality may lead to scheduling conflicts and student dissatisfaction",
            suggested_action="Review constraint priorities and consider relaxing low-priority constraints",
        )]
    elif score < 80:
        return [Recommendation(
            category="quality",
            priority="medium",
            description=f"Quality score ({score}/100) could be improved",
            impact="Moderate quality with room for optimization",
            suggested_action="Run additional optimization iterations with refined parameters",
        )]
    return []


def _recommend_load_balancing(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict,
) -> list[Recommendation]:
    teacher_counts: dict[uuid.UUID, int] = defaultdict(int)
    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        teacher_counts[state.assignments[idx].teacher_id] += 1

    if not teacher_counts:
        return []

    counts = list(teacher_counts.values())
    avg = sum(counts) / len(counts)
    max_count = max(counts)
    min_count = min(counts)

    recommendations = []
    if max_count > avg * 1.5:
        overloaded = [tid for tid, c in teacher_counts.items() if c > avg * 1.5]
        for tid in overloaded[:3]:
            t = state.teachers.get(tid)
            recommendations.append(Recommendation(
                category="load_balance",
                priority="medium",
                description=f"Teacher '{t.full_name if t else tid}' has {teacher_counts[tid]} slots (avg: {avg:.0f})",
                impact="Uneven distribution may cause burnout and reduce teaching quality",
                suggested_action="Redistribute subjects among under-utilized teachers",
            ))

    if min_count < avg * 0.5 and len(teacher_counts) > 1:
        underloaded = [tid for tid, c in teacher_counts.items() if c < avg * 0.5]
        for tid in underloaded[:2]:
            t = state.teachers.get(tid)
            recommendations.append(Recommendation(
                category="load_balance",
                priority="low",
                description=f"Teacher '{t.full_name if t else tid}' has only {teacher_counts[tid]} slots (avg: {avg:.0f})",
                impact="Under-utilized faculty resources",
                suggested_action="Consider assigning additional subjects",
            ))

    return recommendations


def _recommend_distribution(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict,
) -> list[Recommendation]:
    section_days: dict[uuid.UUID, set[str]] = defaultdict(set)
    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        assignment = state.assignments[idx]
        slot = slot_map.get(slot_id)
        if slot:
            section_days[assignment.section_id].add(slot.day_of_week)

    recommendations = []
    for sid, days in section_days.items():
        if len(days) <= 2 and len([i for i, s in solution.items() if s is not None and state.assignments[i].section_id == sid]) >= 5:
            recommendations.append(Recommendation(
                category="distribution",
                priority="medium",
                description=f"Section {sid} classes concentrated on {len(days)} day(s)",
                impact="Poor weekly distribution affects student learning retention",
                suggested_action="Spread subjects more evenly across available days",
            ))

    return recommendations


def _recommend_idle_time(
    state: CSPState,
    solution: dict[int, uuid.UUID],
    slot_map: dict,
) -> list[Recommendation]:
    section_day_times: dict = defaultdict(list)
    for idx, slot_id in solution.items():
        if slot_id is None:
            continue
        assignment = state.assignments[idx]
        slot = slot_map.get(slot_id)
        if slot:
            section_day_times[(assignment.section_id, slot.day_of_week)].append(
                parse_minutes(slot.start_time)
            )

    recommendations = []
    for (sid, day), times in section_day_times.items():
        times.sort()
        for i in range(len(times) - 1):
            gap = times[i + 1] - times[i]
            if gap > 120:
                recommendations.append(Recommendation(
                    category="idle_time",
                    priority="low",
                    description=f"Large gap ({gap // 60}h{gap % 60}m) in section schedule on {day}",
                    impact="Long idle periods waste student time on campus",
                    suggested_action="Consolidate classes to reduce gaps between sessions",
                ))
                break

    return recommendations[:3]


def _recommend_teacher_availability(state: CSPState) -> list[Recommendation]:
    recommendations = []
    for tid, teacher in state.teachers.items():
        if teacher.unavailable and len(teacher.unavailable) > 5:
            recommendations.append(Recommendation(
                category="availability",
                priority="low",
                description=f"Teacher '{teacher.full_name}' has {len(teacher.unavailable)} unavailable slots",
                impact="Limited availability constrains scheduling flexibility",
                suggested_action="Review and reduce unavailability if possible",
            ))

    return recommendations[:3]


def _recommend_resource_usage(state: CSPState, score: float) -> list[Recommendation]:
    total_rooms = len(state.classrooms) + len(state.laboratories)
    if total_rooms == 0:
        return []
    if score < 50:
        return [Recommendation(
            category="resources",
            priority="medium",
            description=f"{total_rooms} rooms available but quality score is low",
            impact="Under-utilized resources affect schedule quality",
            suggested_action="Ensure room capacity matches section strength requirements",
        )]
    return []
