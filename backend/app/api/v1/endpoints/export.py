import uuid
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session, require_role

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/formats")
async def get_export_formats():
    return {
        "formats": [
            {"id": "pdf", "name": "PDF Document", "extension": ".pdf"},
            {"id": "xlsx", "name": "Excel Workbook", "extension": ".xlsx"},
            {"id": "csv", "name": "CSV File", "extension": ".csv"},
        ]
    }


@router.post("/timetable/{timetable_id}")
async def export_timetable(
    timetable_id: uuid.UUID,
    format: str = "pdf",
    session: AsyncSession = Depends(get_db_session),
    _: str = Depends(require_role("viewer")),
):
    timestamp = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"timetable_{timetable_id}_{timestamp}.{format}"

    csv_content = "Timetable Export\n"
    csv_content += f"ID: {timetable_id}\n"
    csv_content += f"Format: {format}\n"

    return Response(
        content=csv_content,
        media_type="text/csv" if format == "csv" else "application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
