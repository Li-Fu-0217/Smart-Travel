"""家庭绑定出入参（见施工规范 §4.5、§5.2）。"""
from pydantic import Field

from app.common.result import CamelModel, DateTimeStr


class FamilyBindRequest(CamelModel):
    name: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=1, max_length=20)
    relation: str | None = Field(None, max_length=20)
    is_primary: int = 1


class FamilyAdminBindRequest(CamelModel):
    user_id: int
    traveler_id: int
    relation: str | None = Field(None, max_length=20)
    is_primary: int = 1


class FamilyBindingVO(CamelModel):
    id: int
    user_id: int
    traveler_id: int
    relation: str | None = None
    is_primary: int = 0
    username: str | None = None
    traveler_name: str | None = None
    create_time: DateTimeStr | None = None
