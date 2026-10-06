"""行程与待办出入参（见施工规范 §4.5、§4.11、§5.2）。"""
from datetime import date, datetime
from decimal import Decimal
from typing import List

from pydantic import Field, field_validator

from app.common.constants import TODO_CATEGORIES
from app.common.result import CamelModel, DateTimeStr


class TripCreateRequest(CamelModel):
    traveler_id: int
    title: str | None = Field(None, max_length=100)
    destination: str | None = Field(None, max_length=100)
    start_date: date | None = None
    end_date: date | None = None
    budget: Decimal | None = None
    remark: str | None = Field(None, max_length=500)
    status: int = 1


class TripUpdateRequest(CamelModel):
    title: str | None = Field(None, max_length=100)
    destination: str | None = Field(None, max_length=100)
    start_date: date | None = None
    end_date: date | None = None
    budget: Decimal | None = None
    remark: str | None = Field(None, max_length=500)
    status: int | None = None


class TripVO(CamelModel):
    id: int
    traveler_id: int
    title: str | None = None
    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    budget: Decimal | None = None
    remark: str | None = None
    status: int = 1
    source_template_id: int | None = None
    create_time: DateTimeStr | None = None
    update_time: DateTimeStr | None = None


class TodoCreateRequest(CamelModel):
    trip_id: int
    item_name: str = Field(..., min_length=1, max_length=200)
    due_time: datetime | None = None
    category: str = "other"

    @field_validator("category")
    @classmethod
    def _check_category(cls, v: str) -> str:
        if v not in TODO_CATEGORIES:
            raise ValueError("待办分类不合法")
        return v


class TodoUpdateRequest(CamelModel):
    item_name: str | None = Field(None, max_length=200)
    due_time: datetime | None = None
    category: str | None = None

    @field_validator("category")
    @classmethod
    def _check_category(cls, v: str | None) -> str | None:
        if v is not None and v not in TODO_CATEGORIES:
            raise ValueError("待办分类不合法")
        return v


class TodoVO(CamelModel):
    id: int
    trip_id: int
    traveler_id: int
    item_name: str
    due_time: DateTimeStr | None = None
    category: str = "other"
    status: int = 2
    done_time: DateTimeStr | None = None
    create_time: DateTimeStr | None = None


class TripTodayTodoItemVO(CamelModel):
    id: int
    item_name: str
    time_slot: str | None = None
    status: int = 2


class TripTodayOverdueItemVO(CamelModel):
    id: int
    item_name: str
    due_time: DateTimeStr | None = None
    status: int = 2


class TripNextDayVO(CamelModel):
    date: date
    items: List[str] = []


class TripTodayBookingVO(CamelModel):
    id: int
    catalog_name: str | None = None
    booking_time: DateTimeStr | None = None
    status: str


class TripTodayVO(CamelModel):
    trip_id: int | None = None
    title: str | None = None
    destination: str | None = None
    day_index: int = 0
    day_count: int = 0
    date: date
    today_todos: List[TripTodayTodoItemVO] = []
    overdue_todos: List[TripTodayOverdueItemVO] = []
    next_days: List[TripNextDayVO] = []
    bookings: List[TripTodayBookingVO] = []
