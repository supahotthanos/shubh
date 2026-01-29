from pydantic import BaseModel, ConfigDict
from typing import Generic, TypeVar, List, Optional
from datetime import datetime

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, items: List[T], total: int, page: int, page_size: int):
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
        )


class TimestampSchema(BaseSchema):
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    message: str
    success: bool = True
