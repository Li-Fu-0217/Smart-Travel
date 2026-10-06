"""用户管理出入参（见施工规范 §4.5）。"""
from pydantic import Field, field_validator

from app.common.result import CamelModel


class UserCreateRequest(CamelModel):
    username: str = Field(..., max_length=50)
    password: str = Field(..., max_length=100)
    role: str = "USER"
    status: int = 1

    @field_validator("role")
    @classmethod
    def _check_role(cls, v: str) -> str:
        if v not in ("ADMIN", "USER"):
            raise ValueError("角色取值不合法")
        return v

    @field_validator("status")
    @classmethod
    def _check_status(cls, v: int) -> int:
        if v not in (0, 1):
            raise ValueError("状态取值不合法")
        return v


class UserUpdateRequest(CamelModel):
    role: str = "USER"
    status: int = 1

    @field_validator("role")
    @classmethod
    def _check_role(cls, v: str) -> str:
        if v not in ("ADMIN", "USER"):
            raise ValueError("角色取值不合法")
        return v

    @field_validator("status")
    @classmethod
    def _check_status(cls, v: int) -> int:
        if v not in (0, 1):
            raise ValueError("状态取值不合法")
        return v
