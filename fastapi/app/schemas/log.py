"""日志出入参（见施工规范 §4.5）。"""
from typing import Optional

from app.common.result import CamelModel, DateTimeStr


class LoginLogVO(CamelModel):
    id: int
    username: Optional[str] = None
    ip: Optional[str] = None
    status: int
    message: Optional[str] = None
    create_time: DateTimeStr | None = None


class OperationLogVO(CamelModel):
    id: int
    username: Optional[str] = None
    module: Optional[str] = None
    action: Optional[str] = None
    method: Optional[str] = None
    url: Optional[str] = None
    ip: Optional[str] = None
    cost_ms: Optional[int] = None
    status: int
    create_time: DateTimeStr | None = None
