"""旅游记录出入参（见施工规范 §4.5、§5.8）。"""
from datetime import date

from pydantic import Field

from app.common.result import CamelModel, DateTimeStr


class RecordCreateRequest(CamelModel):
    traveler_id: int
    trip_id: int | None = None
    destination: str | None = Field(None, max_length=100)
    visited_date: date | None = None
    rating: int | None = Field(None, ge=1, le=5)
    content: str | None = Field(None, max_length=1000)
    photos: str | None = Field(None, max_length=1000)
    visibility: int = Field(0, ge=0, le=1)


class RecordUpdateRequest(CamelModel):
    trip_id: int | None = None
    destination: str | None = Field(None, max_length=100)
    visited_date: date | None = None
    rating: int | None = Field(None, ge=1, le=5)
    content: str | None = Field(None, max_length=1000)
    photos: str | None = Field(None, max_length=1000)
    visibility: int | None = Field(None, ge=0, le=1)


class RecordVO(CamelModel):
    id: int
    traveler_id: int
    traveler_name: str | None = None
    trip_id: int | None = None
    destination: str | None = None
    visited_date: date | None = None
    rating: int | None = None
    content: str | None = None
    photos: str | None = None
    visibility: int = 0
    create_time: DateTimeStr | None = None
