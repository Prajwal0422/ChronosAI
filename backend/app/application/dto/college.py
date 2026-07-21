from pydantic import BaseModel, Field
from app.application.dto.responses import ResponseBase


class CollegeCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    college_type: str = Field(default="degree", max_length=50)
    address: str | None = Field(None, max_length=1000)
    phone: str | None = Field(None, max_length=50)
    email: str | None = Field(None, max_length=255)
    website: str | None = Field(None, max_length=255)
    academic_year: str = Field(..., max_length=20)


class CollegeUpdateRequest(BaseModel):
    name: str | None = Field(None, max_length=255)
    address: str | None = Field(None, max_length=1000)
    phone: str | None = Field(None, max_length=50)
    email: str | None = Field(None, max_length=255)
    website: str | None = Field(None, max_length=255)
    academic_year: str | None = Field(None, max_length=20)


class CollegeResponse(ResponseBase):
    id: str
    name: str
    code: str
    college_type: str
    address: str | None
    phone: str | None
    email: str | None
    website: str | None
    logo_url: str | None
    academic_year: str
    is_active: bool
