"""旅行者档案出入参（见施工规范 §4.5、§5.2）。"""
from datetime import date

from pydantic import Field

from app.common.result import CamelModel, DateTimeStr


class TravelerCreateRequest(CamelModel):
    name: str = Field(..., min_length=1, max_length=50)
    gender: str | None = Field(None, max_length=10)
    birth_date: date | None = None
    phone: str | None = Field(None, max_length=20)
    id_card_no: str | None = Field(None, max_length=30)
    dietary_restrictions: str | None = Field(None, max_length=255)
    allergies: str | None = Field(None, max_length=255)
    mobility_notes: str | None = Field(None, max_length=255)
    preferences: str | None = Field(None, max_length=500)
    emergency_contact: str | None = Field(None, max_length=50)
    emergency_phone: str | None = Field(None, max_length=20)
    status: int = 1


class TravelerUpdateRequest(CamelModel):
    name: str | None = Field(None, max_length=50)
    gender: str | None = Field(None, max_length=10)
    birth_date: date | None = None
    phone: str | None = Field(None, max_length=20)
    id_card_no: str | None = Field(None, max_length=30)
    dietary_restrictions: str | None = Field(None, max_length=255)
    allergies: str | None = Field(None, max_length=255)
    mobility_notes: str | None = Field(None, max_length=255)
    preferences: str | None = Field(None, max_length=500)
    emergency_contact: str | None = Field(None, max_length=50)
    emergency_phone: str | None = Field(None, max_length=20)
    status: int | None = None


class TravelerVO(CamelModel):
    id: int
    name: str
    gender: str | None = None
    birth_date: date | None = None
    phone: str | None = None
    status: int = 1
    preferences: str | None = None
    preference_tags: str | None = None
    create_time: DateTimeStr | None = None
    update_time: DateTimeStr | None = None


class TravelerProfileVO(CamelModel):
    id: int
    name: str
    gender: str | None = None
    birth_date: date | None = None
    phone: str | None = None
    id_card_no: str | None = None
    dietary_restrictions: str | None = None
    allergies: str | None = None
    mobility_notes: str | None = None
    preferences: str | None = None
    preference_tags: str | None = None
    preference_summary: str | None = None
    preference_updated_at: DateTimeStr | None = None
    emergency_contact: str | None = None
    emergency_phone: str | None = None
    status: int = 1
    create_time: DateTimeStr | None = None
    update_time: DateTimeStr | None = None
