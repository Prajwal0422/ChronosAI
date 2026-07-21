from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    PRINCIPAL = "principal"
    HOD = "hod"
    COORDINATOR = "coordinator"
    FACULTY = "faculty"
    VIEWER = "viewer"


class CollegeType(str, Enum):
    SCHOOL = "school"
    PU = "pu"
    DEGREE = "degree"
    ENGINEERING = "engineering"
    UNIVERSITY = "university"


class SubjectType(str, Enum):
    THEORY = "theory"
    LAB = "lab"
    PRACTICAL = "practical"
    TUTORIAL = "tutorial"


class SlotType(str, Enum):
    LECTURE = "lecture"
    LAB = "lab"
    BREAK = "break"
    LUNCH = "lunch"


class RoomType(str, Enum):
    LECTURE = "lecture"
    LAB = "lab"
    SEMINAR = "seminar"
    TUTORIAL = "tutorial"


class TimetableStatus(str, Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ConstraintType(str, Enum):
    HARD = "hard"
    SOFT = "soft"


class ConstraintCategory(str, Enum):
    TEACHER = "teacher"
    ROOM = "room"
    TIME = "time"
    SUBJECT = "subject"
    INSTITUTIONAL = "institutional"


class ConflictType(str, Enum):
    TEACHER_OVERLAP = "teacher_overlap"
    ROOM_OVERLAP = "room_overlap"
    LAB_OVERLAP = "lab_overlap"
    CONSTRAINT_VIOLATION = "constraint_violation"
    DUPLICATE_ENTRY = "duplicate_entry"


class ConflictSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DayOfWeek(str, Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class HolidayType(str, Enum):
    PUBLIC = "public"
    COLLEGE = "college"
    DEPARTMENT = "department"


class ApprovalStatus(str, Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class NotificationType(str, Enum):
    GENERATION_COMPLETED = "generation_completed"
    CONFLICT_DETECTED = "conflict_detected"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_APPROVED = "approval_approved"
    APPROVAL_REJECTED = "approval_rejected"
    SCHEDULE_CHANGED = "schedule_changed"
    SIMULATION_COMPLETED = "simulation_completed"
    SYSTEM_ALERT = "system_alert"
    IMPORT_COMPLETED = "import_completed"
    EXPORT_COMPLETED = "export_completed"
    VERSION_CREATED = "version_created"


class SimulationType(str, Enum):
    TEACHER_UNAVAILABLE = "teacher_unavailable"
    NEW_CLASSROOM = "new_classroom"
    HOLIDAY_DECLARED = "holiday_declared"
    ADDITIONAL_SECTION = "additional_section"
    FACULTY_RESIGNED = "faculty_resigned"
    LABORATORY_UNAVAILABLE = "laboratory_unavailable"
    CONSTRAINT_CHANGED = "constraint_changed"
    TIME_SLOT_CHANGED = "time_slot_changed"
    CUSTOM = "custom"


class EventAction(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    GENERATE = "generate"
    IMPORT = "import"
    EXPORT = "export"
    PUBLISH = "publish"
    ARCHIVE = "archive"
    APPROVE = "approve"
    REVIEW = "review"
    SIMULATE = "simulate"
    VERSION_CREATE = "version_create"
    VERSION_RESTORE = "version_restore"
    SWAP = "swap"
    RESOLVE = "resolve"
