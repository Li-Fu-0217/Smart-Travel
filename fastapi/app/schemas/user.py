"""用户管理出入参（见施工规范 §4.5）。"""
from pydantic import Field

from app.common.result import CamelModel


class UserCreateRequest(CamelModel):
    username: str = Field(..., max_length=50)
    password: str = Field(..., max_length=100)
    role: str = "USER"
    status: int = 1


class UserUpdateRequest(CamelModel):
    role: str = "USER"
    status: int = 1
