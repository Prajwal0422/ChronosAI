import asyncio
import os
import uuid
from typing import AsyncGenerator, AsyncIterator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_integration.db"

from app.main import app  # noqa: E402
from app.infrastructure.database.base import Base  # noqa: E402
from app.infrastructure.database.models import *  # noqa: E401, F403  # noqa: E402
from app.api.v1.deps import get_db_session, get_current_user_id, get_current_user_role  # noqa: E402
from app.core.security import create_access_token, hash_password  # noqa: E402
from app.core.constants import UserRole, CollegeType, SlotType, SubjectType, DayOfWeek, RoomType  # noqa: E402

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_integration.db"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db_session] = lambda: db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def auth_client(client: AsyncClient, db_session: AsyncSession) -> AsyncClient:
    from app.infrastructure.database.models import UserModel
    user = UserModel(
        email="admin@test.edu",
        password_hash=hash_password("admin123"),
        full_name="Admin User",
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    await db_session.flush()

    app.dependency_overrides[get_current_user_id] = lambda: str(user.id)
    app.dependency_overrides[get_current_user_role] = lambda: UserRole.ADMIN.value
    return client


@pytest_asyncio.fixture(scope="function")
async def viewer_client(client: AsyncClient, db_session: AsyncSession) -> AsyncClient:
    from app.infrastructure.database.models import UserModel
    user = UserModel(
        email="viewer@test.edu",
        password_hash=hash_password("viewer123"),
        full_name="Viewer User",
        role=UserRole.VIEWER,
    )
    db_session.add(user)
    await db_session.flush()

    app.dependency_overrides[get_current_user_id] = lambda: str(user.id)
    app.dependency_overrides[get_current_user_role] = lambda: UserRole.VIEWER.value
    return client


@pytest_asyncio.fixture(scope="function")
async def seed_college(db_session: AsyncSession):
    from app.infrastructure.database.models import CollegeModel
    college = CollegeModel(
        name="Test Engineering College",
        code="TEC001",
        college_type=CollegeType.ENGINEERING,
        academic_year="2025-2026",
    )
    db_session.add(college)
    await db_session.flush()
    return college


@pytest_asyncio.fixture(scope="function")
async def seed_department(db_session: AsyncSession, seed_college):
    from app.infrastructure.database.models import DepartmentModel
    dept = DepartmentModel(
        college_id=seed_college.id,
        name="Computer Science",
        code="CS",
    )
    db_session.add(dept)
    await db_session.flush()
    return dept


@pytest_asyncio.fixture(scope="function")
async def seed_semester(db_session: AsyncSession, seed_department):
    from app.infrastructure.database.models import SemesterModel
    sem = SemesterModel(
        department_id=seed_department.id,
        name="Semester 1",
        code="SEM1",
        year=1,
        order=1,
    )
    db_session.add(sem)
    await db_session.flush()
    return sem


@pytest_asyncio.fixture(scope="function")
async def seed_section(db_session: AsyncSession, seed_semester):
    from app.infrastructure.database.models import SectionModel
    section = SectionModel(
        semester_id=seed_semester.id,
        name="Section A",
        code="CSA",
        strength=60,
    )
    db_session.add(section)
    await db_session.flush()
    return section


@pytest_asyncio.fixture(scope="function")
async def seed_teacher(db_session: AsyncSession, seed_department):
    from app.infrastructure.database.models import TeacherModel
    teacher = TeacherModel(
        department_id=seed_department.id,
        employee_code="T001",
        full_name="Dr. Smith",
        email="smith@test.edu",
        max_lectures_per_day=4,
        max_lectures_per_week=20,
        max_consecutive_lectures=3,
    )
    db_session.add(teacher)
    await db_session.flush()
    return teacher


@pytest_asyncio.fixture(scope="function")
async def seed_teacher2(db_session: AsyncSession, seed_department):
    from app.infrastructure.database.models import TeacherModel
    teacher = TeacherModel(
        department_id=seed_department.id,
        employee_code="T002",
        full_name="Prof. Jones",
        email="jones@test.edu",
        max_lectures_per_day=3,
        max_lectures_per_week=15,
        max_consecutive_lectures=2,
    )
    db_session.add(teacher)
    await db_session.flush()
    return teacher


@pytest_asyncio.fixture(scope="function")
async def seed_subject(db_session: AsyncSession, seed_department):
    from app.infrastructure.database.models import SubjectModel
    subject = SubjectModel(
        department_id=seed_department.id,
        name="Mathematics",
        code="MTH101",
        subject_type=SubjectType.THEORY,
        lectures_per_week=3,
    )
    db_session.add(subject)
    await db_session.flush()
    return subject


@pytest_asyncio.fixture(scope="function")
async def seed_subject2(db_session: AsyncSession, seed_department):
    from app.infrastructure.database.models import SubjectModel
    subject = SubjectModel(
        department_id=seed_department.id,
        name="Physics Lab",
        code="PHY101",
        subject_type=SubjectType.LAB,
        lectures_per_week=2,
        is_lab=True,
        lab_duration=2,
    )
    db_session.add(subject)
    await db_session.flush()
    return subject


@pytest_asyncio.fixture(scope="function")
async def seed_subject_assignment(db_session: AsyncSession, seed_section, seed_subject, seed_teacher):
    from app.infrastructure.database.models import SubjectAssignmentModel
    sa = SubjectAssignmentModel(
        section_id=seed_section.id,
        subject_id=seed_subject.id,
        teacher_id=seed_teacher.id,
    )
    db_session.add(sa)
    await db_session.flush()
    return sa


@pytest_asyncio.fixture(scope="function")
async def seed_classroom(db_session: AsyncSession, seed_college):
    from app.infrastructure.database.models import ClassroomModel
    room = ClassroomModel(
        college_id=seed_college.id,
        name="Room 101",
        code="R101",
        capacity=60,
        building="Main",
        floor=1,
        room_type=RoomType.LECTURE,
    )
    db_session.add(room)
    await db_session.flush()
    return room


@pytest_asyncio.fixture(scope="function")
async def seed_time_slot(db_session: AsyncSession, seed_college):
    from app.infrastructure.database.models import TimeSlotModel
    slot = TimeSlotModel(
        college_id=seed_college.id,
        name="Monday 08-09",
        day_of_week=DayOfWeek.MONDAY,
        start_time="08:00",
        end_time="09:00",
        slot_type=SlotType.LECTURE,
    )
    db_session.add(slot)
    await db_session.flush()
    return slot


@pytest_asyncio.fixture(scope="function")
async def seed_time_slots(db_session: AsyncSession, seed_college):
    from app.infrastructure.database.models import TimeSlotModel
    slots = []
    for i, (day, st, et) in enumerate([
        (DayOfWeek.MONDAY, "08:00", "09:00"),
        (DayOfWeek.MONDAY, "09:00", "10:00"),
        (DayOfWeek.MONDAY, "10:00", "11:00"),
        (DayOfWeek.TUESDAY, "08:00", "09:00"),
        (DayOfWeek.TUESDAY, "09:00", "10:00"),
        (DayOfWeek.TUESDAY, "14:00", "16:00"),
    ]):
        slot = TimeSlotModel(
            college_id=seed_college.id,
            name=f"{day.value.capitalize()} {st}-{et}",
            day_of_week=day,
            start_time=st,
            end_time=et,
            slot_type=SlotType.LAB if i == 5 else SlotType.LECTURE,
        )
        db_session.add(slot)
        slots.append(slot)
    await db_session.flush()
    return slots


@pytest_asyncio.fixture(scope="function")
async def seed_working_days(db_session: AsyncSession, seed_college):
    from app.infrastructure.database.models import WorkingDayModel
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
        wd = WorkingDayModel(college_id=seed_college.id, day_of_week=day)
        db_session.add(wd)
    await db_session.flush()


@pytest_asyncio.fixture(scope="function")
async def seed_academic_calendar(db_session: AsyncSession, seed_college):
    from app.infrastructure.database.models import AcademicCalendarModel
    from datetime import date
    cal = AcademicCalendarModel(
        college_id=seed_college.id,
        academic_year="2025-2026",
        term_name="Odd Semester",
        start_date=date(2025, 6, 1),
        end_date=date(2026, 5, 31),
    )
    db_session.add(cal)
    await db_session.flush()
    return cal


@pytest_asyncio.fixture(scope="function")
async def seed_timetable(db_session: AsyncSession, seed_section, seed_academic_calendar):
    from app.infrastructure.database.models import TimetableModel
    from app.core.constants import TimetableStatus
    tt = TimetableModel(
        section_id=seed_section.id,
        academic_calendar_id=seed_academic_calendar.id,
        name="CS Section A Timetable",
        status=TimetableStatus.DRAFT,
        version=1,
    )
    db_session.add(tt)
    await db_session.flush()
    return tt
