import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PaginationParams(BaseModel):
    offset: int = 0
    limit: int = 100


class PaginatedResponse(BaseModel):
    items: list
    total: int
    offset: int
    limit: int

    model_config = ConfigDict(from_attributes=True)


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str
    code: str


class ErrorResponse(BaseModel):
    success: bool = False
    code: str
    message: str
    details: list[ErrorDetail] = []
    request_id: str | None = None
    timestamp: datetime | None = None
