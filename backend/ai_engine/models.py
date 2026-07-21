import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SlotType(Enum):
    LECTURE = "lecture"
    LAB = "lab"
    BREAK = "break"
    LUNCH = "lunch"


class ConstraintCategory(str, Enum):
    TEACHER = "teacher"
    ROOM = "room"
    TIME = "time"
    SUBJECT = "subject"
    INSTITUTIONAL = "institutional"


class ConflictSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TimeSlot:
    id: uuid.UUID
    day_of_week: str
    start_time: str
    end_time: str
    slot_type: SlotType
    slot_group: str | None = None


@dataclass
class Teacher:
    id: uuid.UUID
    full_name: str
    max_lectures_per_day: int
    max_lectures_per_week: int
    max_consecutive_lectures: int
    is_shared: bool
    unavailable: list["TimeRange"] = field(default_factory=list)
    preferred_days: list[str] = field(default_factory=list)
    preferred_start_times: list[str] = field(default_factory=list)
    preferred_end_times: list[str] = field(default_factory=list)
    department_id: uuid.UUID | None = None


@dataclass
class Subject:
    id: uuid.UUID
    name: str
    code: str
    subject_type: str
    lectures_per_week: int
    is_elective: bool
    is_lab: bool
    lab_duration: int | None = None
    department_id: uuid.UUID | None = None
    priority: int = 5
    is_fixed: bool = False
    fixed_slot_ids: list[uuid.UUID] = field(default_factory=list)
    morning_only: bool = False
    afternoon_only: bool = False


@dataclass
class Classroom:
    id: uuid.UUID
    capacity: int
    room_type: str
    department_id: uuid.UUID | None = None


@dataclass
class Laboratory:
    id: uuid.UUID
    capacity: int
    department_id: uuid.UUID | None = None


@dataclass
class Section:
    id: uuid.UUID
    name: str
    strength: int
    semester_id: uuid.UUID | None = None
    department_id: uuid.UUID | None = None


@dataclass
class TeachingAssignment:
    section_id: uuid.UUID
    subject_id: uuid.UUID
    teacher_id: uuid.UUID
    subject: Subject
    lectures_per_week: int
    is_lab: bool
    lab_duration: int | None = None


@dataclass
class TimeRange:
    day_of_week: str
    start_time: str
    end_time: str


@dataclass
class CSPVariable:
    assignment_idx: int
    section_id: uuid.UUID
    subject_id: uuid.UUID
    teacher_id: uuid.UUID
    domain: list[uuid.UUID]
    is_lab: bool = False


@dataclass
class CSPState:
    timetable_id: uuid.UUID
    section_id: uuid.UUID
    assignments: list[TeachingAssignment]
    time_slots: list[TimeSlot]
    teachers: dict[uuid.UUID, Teacher]
    subjects: dict[uuid.UUID, Subject]
    classrooms: list[Classroom]
    laboratories: list[Laboratory]
    working_days: set[str]
    holidays: list["HolidayInfo"] = field(default_factory=list)
    hard_constraints: list[dict[str, Any]] = field(default_factory=list)
    soft_constraints: list[dict[str, Any]] = field(default_factory=list)
    break_slots: list[uuid.UUID] = field(default_factory=list)
    lunch_slots: list[uuid.UUID] = field(default_factory=list)
    slot_map: dict[uuid.UUID, TimeSlot] = field(default_factory=dict)


@dataclass
class HolidayInfo:
    date: str
    day_of_week: str
    name: str
    is_public: bool = True


@dataclass
class EntryResult:
    time_slot_id: uuid.UUID
    section_id: uuid.UUID
    teacher_id: uuid.UUID
    subject_id: uuid.UUID
    classroom_id: uuid.UUID | None = None
    laboratory_id: uuid.UUID | None = None
    is_lab_session: bool = False
    notes: str | None = None


@dataclass
class ConflictInfo:
    conflict_type: str
    severity: ConflictSeverity
    description: str
    involved_slots: list[uuid.UUID] = field(default_factory=list)
    involved_teachers: list[uuid.UUID] = field(default_factory=list)
    involved_rooms: list[uuid.UUID] = field(default_factory=list)
    involved_sections: list[uuid.UUID] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class RepairAction:
    action_type: str
    description: str
    assignment_idx: int
    old_slot_id: uuid.UUID | None = None
    new_slot_id: uuid.UUID | None = None
    reason: str = ""


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    coverage_pct: float = 100.0


@dataclass
class Recommendation:
    category: str
    priority: str
    description: str
    impact: str
    suggested_action: str = ""


@dataclass
class GenerationReport:
    score: float = 0.0
    constraint_satisfaction_pct: float = 0.0
    optimization_score: float = 0.0
    detected_conflicts: list[ConflictInfo] = field(default_factory=list)
    repairs_applied: list[RepairAction] = field(default_factory=list)
    generation_time_seconds: float = 0.0
    resource_utilization: dict[str, float] = field(default_factory=dict)
    faculty_load: dict[str, int] = field(default_factory=dict)
    room_utilization: dict[str, float] = field(default_factory=dict)
    reasoning_summary: str = ""
    solutions_generated: int = 0
    solution_selected: str = ""


MIN_SLOT_DURATION_MINUTES = 30
