import uuid
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, model_validator


class ResponseBase(BaseModel):
    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def _coerce_uuid_to_str(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return data
        if not hasattr(data, "__table__"):
            return data
        result = {}
        for col in data.__table__.columns:
            val = getattr(data, col.name)
            if isinstance(val, uuid.UUID):
                val = str(val)
            result[col.name] = val
        return result


T = TypeVar("T")


class PaginatedResponse(BaseModel):
    items: list
    total: int
    offset: int = 0
    limit: int = 100


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Any = None
