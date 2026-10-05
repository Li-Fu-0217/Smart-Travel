"""预约域出入参（见施工规范 §4.5、§4.9、§5.7、§5.8）。"""
from decimal import Decimal
from typing import List

from pydantic import Field, field_validator

from app.common.constants import BOOKING_STATUS, ITEM_TYPES
from app.common.result import CamelModel, DateTimeStr


class BookingCatalogCreateRequest(CamelModel):
    name: str = Field(..., min_length=1, max_length=100)
    item_type: str
    description: str | None = Field(None, max_length=500)
    duration_minutes: int | None = None
    price: Decimal | None = None
    status: int = 1

    @field_validator("item_type")
    @classmethod
    def _check_item_type(cls, v: str) -> str:
        if v not in ITEM_TYPES:
            raise ValueError("预约项目类型不合法")
        return v


class BookingCatalogUpdateRequest(CamelModel):
    name: str | None = Field(None, max_length=100)
    item_type: str | None = None
    description: str | None = Field(None, max_length=500)
    duration_minutes: int | None = None
    price: Decimal | None = None
    status: int | None = None

    @field_validator("item_type")
    @classmethod
    def _check_item_type(cls, v: str | None) -> str | None:
        if v is not None and v not in ITEM_TYPES:
            raise ValueError("预约项目类型不合法")
        return v


class BookingCatalogVO(CamelModel):
    id: int
    name: str
    item_type: str
    description: str | None = None
    duration_minutes: int | None = None
    price: Decimal | None = None
    status: int = 1
    create_time: DateTimeStr | None = None


class BookingSlotVO(CamelModel):
    catalog_id: int
    catalog_name: str
    item_type: str
    duration_minutes: int | None = None
    price: Decimal | None = None
    slots: List[str] = []


class BookingOrderCreateRequest(CamelModel):
    traveler_id: int
    catalog_id: int
    slot: str = Field(..., min_length=1, max_length=50)
    guest_count: int = Field(1, ge=1, le=99)
    remark: str | None = Field(None, max_length=500)


class BookingOrderUpdateRequest(CamelModel):
    status: str | None = None
    version: int
    slot: str | None = Field(None, max_length=50)
    remark: str | None = Field(None, max_length=500)

    @field_validator("status")
    @classmethod
    def _check_status(cls, v: str | None) -> str | None:
        if v is not None and v not in BOOKING_STATUS:
            raise ValueError("订单状态不合法")
        return v


class BookingOrderVO(CamelModel):
    id: int
    traveler_id: int
    catalog_id: int
    catalog_name: str | None = None
    booking_time: DateTimeStr | None = None
    guest_count: int = 1
    status: str = "pending"
    source: str = "manual"
    slot: str | None = None
    version: int = 0
    remark: str | None = None
    create_time: DateTimeStr | None = None
    update_time: DateTimeStr | None = None
