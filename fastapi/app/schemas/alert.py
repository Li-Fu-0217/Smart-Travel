"""旅途求助出入参（见施工规范 §4.5、§5.8）。"""
from pydantic import Field, field_validator

from app.common.constants import ALERT_STATUS, ALERT_TYPES, SOURCES
from app.common.result import CamelModel, DateTimeStr


class AlertCreateRequest(CamelModel):
    traveler_id: int
    location: str | None = Field(None, max_length=255)
    message: str | None = Field(None, max_length=500)
    alert_type: str = "other"
    notify_family: int = 0
    notify_staff: int = 0
    source: str = "manual"

    @field_validator("alert_type")
    @classmethod
    def _check_alert_type(cls, v: str) -> str:
        if v not in ALERT_TYPES:
            raise ValueError("求助类型不合法")
        return v

    @field_validator("source")
    @classmethod
    def _check_source(cls, v: str) -> str:
        if v not in SOURCES:
            raise ValueError("来源不合法")
        return v


class AlertUpdateRequest(CamelModel):
    status: str | None = None

    @field_validator("status")
    @classmethod
    def _check_status(cls, v: str | None) -> str | None:
        if v is not None and v not in ALERT_STATUS:
            raise ValueError("工单状态不合法")
        return v


class AlertVO(CamelModel):
    id: int
    traveler_id: int
    traveler_name: str | None = None
    location: str | None = None
    message: str | None = None
    alert_type: str = "other"
    status: str = "open"
    notify_family: int = 0
    notify_staff: int = 0
    source: str = "manual"
    create_time: DateTimeStr | None = None
