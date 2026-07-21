from fastapi import APIRouter

api_router = APIRouter()

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.colleges import router as colleges_router
from app.api.v1.endpoints.departments import router as departments_router
from app.api.v1.endpoints.semesters import router as semesters_router
from app.api.v1.endpoints.sections import router as sections_router
from app.api.v1.endpoints.teachers import router as teachers_router
from app.api.v1.endpoints.subjects import router as subjects_router
from app.api.v1.endpoints.classrooms import router as classrooms_router
from app.api.v1.endpoints.laboratories import router as laboratories_router
from app.api.v1.endpoints.time_slots import router as time_slots_router
from app.api.v1.endpoints.calendar import calendar_router, working_days_router, holidays_router
from app.api.v1.endpoints.constraints import router as constraints_router
from app.api.v1.endpoints.timetables import router as timetables_router
from app.api.v1.endpoints.conflicts import router as conflicts_router
from app.api.v1.endpoints.import_timetable import router as import_router
from app.api.v1.endpoints.export import router as export_router
from app.api.v1.endpoints.analytics import router as analytics_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.settings import router as settings_router
from app.api.v1.endpoints.profiles import router as profiles_router
from app.api.v1.endpoints.insights import router as insights_router
from app.api.v1.endpoints.health_score import router as health_score_router
from app.api.v1.endpoints.simulation import router as simulation_router
from app.api.v1.endpoints.versions import router as versions_router
from app.api.v1.endpoints.approvals import router as approvals_router
from app.api.v1.endpoints.audit_logs import router as audit_logs_router
from app.api.v1.endpoints.notifications import router as notifications_router
from app.api.v1.endpoints.search import router as search_router

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(colleges_router)
api_router.include_router(departments_router)
api_router.include_router(semesters_router)
api_router.include_router(sections_router)
api_router.include_router(teachers_router)
api_router.include_router(subjects_router)
api_router.include_router(classrooms_router)
api_router.include_router(laboratories_router)
api_router.include_router(time_slots_router)
api_router.include_router(calendar_router)
api_router.include_router(working_days_router)
api_router.include_router(holidays_router)
api_router.include_router(constraints_router)
api_router.include_router(timetables_router)
api_router.include_router(conflicts_router)
api_router.include_router(import_router)
api_router.include_router(export_router)
api_router.include_router(analytics_router)
api_router.include_router(dashboard_router)
api_router.include_router(settings_router)
api_router.include_router(profiles_router)
api_router.include_router(insights_router)
api_router.include_router(health_score_router)
api_router.include_router(simulation_router)
api_router.include_router(versions_router)
api_router.include_router(approvals_router)
api_router.include_router(audit_logs_router)
api_router.include_router(notifications_router)
api_router.include_router(search_router)
