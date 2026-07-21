import pytest
from datetime import datetime, timezone

from app.core.constants import (
    UserRole, CollegeType, SubjectType, SlotType, RoomType,
    TimetableStatus, ConstraintType, ConstraintCategory,
    ConflictType, ConflictSeverity, HolidayType,
)


class TestEnums:
    def test_user_role_values(self):
        assert UserRole.ADMIN == "admin"
        assert UserRole.PRINCIPAL == "principal"
        assert UserRole.HOD == "hod"
        assert UserRole.COORDINATOR == "coordinator"
        assert UserRole.FACULTY == "faculty"
        assert UserRole.VIEWER == "viewer"

    def test_college_type_values(self):
        assert CollegeType.SCHOOL == "school"
        assert CollegeType.PU == "pu"
        assert CollegeType.DEGREE == "degree"
        assert CollegeType.ENGINEERING == "engineering"
        assert CollegeType.UNIVERSITY == "university"

    def test_subject_type_values(self):
        assert SubjectType.THEORY == "theory"
        assert SubjectType.LAB == "lab"
        assert SubjectType.PRACTICAL == "practical"
        assert SubjectType.TUTORIAL == "tutorial"

    def test_slot_type_values(self):
        assert SlotType.LECTURE == "lecture"
        assert SlotType.LAB == "lab"
        assert SlotType.BREAK == "break"
        assert SlotType.LUNCH == "lunch"

    def test_timetable_status_values(self):
        assert TimetableStatus.DRAFT == "draft"
        assert TimetableStatus.GENERATED == "generated"
        assert TimetableStatus.PUBLISHED == "published"
        assert TimetableStatus.ARCHIVED == "archived"

    def test_conflict_type_values(self):
        assert ConflictType.TEACHER_OVERLAP == "teacher_overlap"
        assert ConflictType.ROOM_OVERLAP == "room_overlap"

    def test_holiday_type_values(self):
        assert HolidayType.PUBLIC == "public"
        assert HolidayType.COLLEGE == "college"
        assert HolidayType.DEPARTMENT == "department"


class TestBaseModel:
    def test_abstract_base(self):
        from app.infrastructure.database.base import BaseModel
        assert BaseModel.__abstract__ is True

    def test_timestamp_defaults(self):
        from app.infrastructure.database.models import UserModel
        assert hasattr(UserModel, "created_at")
        assert hasattr(UserModel, "updated_at")
        assert hasattr(UserModel, "is_active")

    def test_soft_delete_fields(self):
        from app.infrastructure.database.models import UserModel
        assert hasattr(UserModel, "deleted_at")
        assert hasattr(UserModel, "is_active")
