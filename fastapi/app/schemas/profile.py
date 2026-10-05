"""个人中心出入参（见施工规范 §4.8）。"""
from pydantic import Field

from app.common.result import CamelModel


class ProfileUpdateRequest(CamelModel):
    nickname: str | None = Field(None, max_length=50)
    email: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=20)


class AvatarUpdateRequest(CamelModel):
    avatar: str = Field(..., max_length=255)


class PasswordUpdateRequest(CamelModel):
    old_password: str = Field(..., max_length=100)
    new_password: str = Field(..., min_length=6, max_length=100)
