"""认证出入参（见施工规范 §4.5）。"""
from pydantic import Field

from app.common.result import CamelModel, DateTimeStr


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
    create_time: DateTimeStr | None = None
    update_time: DateTimeStr | None = None


class LoginResponse(CamelModel):
    token: str
    user: UserVO
