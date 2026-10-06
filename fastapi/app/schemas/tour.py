"""拼团活动出入参（见施工规范 §4.5、§5.8）。"""
from datetime import datetime

from pydantic import Field, field_validator

from app.common.result import CamelModel, DateTimeStr


class TourCreateRequest(CamelModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str | None = Field(None, max_length=2000)
    destination: str | None = Field(None, max_length=100)
    start_time: datetime | None = None
    end_time: datetime | None = None
    capacity: int = Field(0, ge=0)
    status: int = 1
    @field_validator("status")
    @classmethod
    def _check_status(cls, v: int | None) -> int | None:
        if v is not None and v not in (0, 1):
            raise ValueError("状态取值不合法")
        return v


class TourUpdateRequest(CamelModel):
    title: str | None = Field(None, max_length=100)
    content: str | None = Field(None, max_length=2000)
    destination: str | None = Field(None, max_length=100)
    start_time: datetime | None = None
    end_time: datetime | None = None
    capacity: int | None = Field(None, ge=0)
    status: int | None = None
    @field_validator("status")
    @classmethod
    def _check_status(cls, v: int | None) -> int | None:
        if v is not None and v not in (0, 1):
            raise ValueError("状态取值不合法")
        return v


class SignupRequest(CamelModel):
    traveler_id: int


class TourVO(CamelModel):
    id: int
    title: str
    content: str | None = None
    destination: str | None = None
    start_time: DateTimeStr | None = None
    end_time: DateTimeStr | None = None
    capacity: int = 0
    status: int = 1
    create_time: DateTimeStr | None = None


class SignupVO(CamelModel):
    id: int
    tour_id: int
    traveler_id: int
    user_id: int
    status: str = "registered"
    tour_title: str | None = None
    traveler_name: str | None = None
    username: str | None = None
    create_time: DateTimeStr | None = None
