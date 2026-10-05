"""认证出入参（见施工规范 §4.5）。"""
from datetime import datetime
from typing import Optional

from pydantic import Field, field_serializer

from app.common.result import CamelModel


class CaptchaResponse(CamelModel):
    captcha_id: str
    image: str


class LoginRequest(CamelModel):
    username: str = Field(..., max_length=50)
    password: str = Field(..., max_length=100)
    captcha_id: str
    captcha_code: str


class RegisterRequest(CamelModel):
    username: str = Field(..., max_length=50)
    password: str = Field(..., max_length=100)
    captcha_id: str
    captcha_code: str


class UserVO(CamelModel):
    id: int
    username: str
    role: str
    status: int
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    @field_serializer("create_time", "update_time")
    def _fmt_dt(self, v, _info):
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else None


class LoginResponse(CamelModel):
    token: str
    user: UserVO
