from pydantic import BaseModel, Field
from app.application.dto.responses import ResponseBase


class DepartmentCreateRequest(BaseModel):
    college_id: str
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    hod_id: str | None = None
    description: str | None = Field(None, max_length=1000)


class DepartmentUpdateRequest(BaseModel):
    name: str | None = Field(None, max_length=255)
    hod_id: str | None = None
    description: str | None = Field(None, max_length=1000)


class DepartmentResponse(ResponseBase):
    id: str
    college_id: str
    name: str
    code: str
    hod_id: str | None
    description: str | None
    is_active: bool
