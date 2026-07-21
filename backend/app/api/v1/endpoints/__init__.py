import uuid
from typing import Any

from fastapi import Query

from app.application.dto.responses import PaginatedResponse, SuccessResponse


def pagination_params(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    sort_by: str | None = Query(None),
    sort_order: str = Query("desc"),
) -> dict:
    return {"offset": offset, "limit": limit, "sort_by": sort_by, "sort_order": sort_order}


def to_paginated_response(items: list, total: int, offset: int, limit: int) -> dict:
    return {
        "items": items,
        "total": total,
        "offset": offset,
        "limit": limit,
    }
