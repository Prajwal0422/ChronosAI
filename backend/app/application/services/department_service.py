from app.application.services.base_service import BaseService
from app.infrastructure.database.models import DepartmentModel
from app.infrastructure.database.repositories.base import BaseRepository


class DepartmentService(BaseService):
    def __init__(self, session):
        repo = BaseRepository(DepartmentModel, session)
        super().__init__(repo, session)


class SemesterService(BaseService):
    def __init__(self, session):
        from app.infrastructure.database.models import SemesterModel
        repo = BaseRepository(SemesterModel, session)
        super().__init__(repo, session)


class SectionService(BaseService):
    def __init__(self, session):
        from app.infrastructure.database.models import SectionModel
        repo = BaseRepository(SectionModel, session)
        super().__init__(repo, session)


class TeacherService(BaseService):
    def __init__(self, session):
        from app.infrastructure.database.models import TeacherModel
        repo = BaseRepository(TeacherModel, session)
        super().__init__(repo, session)


class SubjectService(BaseService):
    def __init__(self, session):
        from app.infrastructure.database.models import SubjectModel
        repo = BaseRepository(SubjectModel, session)
        super().__init__(repo, session)


class ClassroomService(BaseService):
    def __init__(self, session):
        from app.infrastructure.database.models import ClassroomModel
        repo = BaseRepository(ClassroomModel, session)
        super().__init__(repo, session)


class LaboratoryService(BaseService):
    def __init__(self, session):
        from app.infrastructure.database.models import LaboratoryModel
        repo = BaseRepository(LaboratoryModel, session)
        super().__init__(repo, session)


class TimeSlotService(BaseService):
    def __init__(self, session):
        from app.infrastructure.database.models import TimeSlotModel
        repo = BaseRepository(TimeSlotModel, session)
        super().__init__(repo, session)


class AcademicCalendarService(BaseService):
    def __init__(self, session):
        from app.infrastructure.database.models import AcademicCalendarModel
        repo = BaseRepository(AcademicCalendarModel, session)
        super().__init__(repo, session)


class WorkingDayService(BaseService):
    def __init__(self, session):
        from app.infrastructure.database.models import WorkingDayModel
        repo = BaseRepository(WorkingDayModel, session)
        super().__init__(repo, session)


class HolidayService(BaseService):
    def __init__(self, session):
        from app.infrastructure.database.models import HolidayModel
        repo = BaseRepository(HolidayModel, session)
        super().__init__(repo, session)
