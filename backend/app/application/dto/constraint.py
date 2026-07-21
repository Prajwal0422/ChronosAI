from pydantic import BaseModel, Field
from app.application.dto.responses import ResponseBase


class ConstraintCreateRequest(BaseModel):
    college_id: str
    department_id: str | None = None
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    constraint_type: str
    category: str
    priority: int = 0
    config: dict = Field(default_factory=dict)


class ConstraintUpdateRequest(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=1000)
    constraint_type: str | None = None
    priority: int | None = None
    config: dict | None = None
    is_active: bool | None = None


class ConstraintResponse(ResponseBase):
    id: str
    college_id: str
    department_id: str | None
    name: str
    description: str | None
    constraint_type: str
    category: str
    priority: int
    config: dict
    is_active: bool
