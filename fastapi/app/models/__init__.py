"""系统表 SQLModel 映射（见施工规范 §9 阶段 1、§5.6）。
仅映射 5 张系统表；业务表（17 张）在 models/travel.py，属阶段 3。
唯一约束与索引只写在 sql/system.sql，此处不重复声明。
时间字段用 datetime = Field(default_factory=datetime.now)（update_time 加 onupdate）。
"""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class SysUser(SQLModel, table=True):
    __tablename__ = "sys_user"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password: str
    role: str = "USER"
    status: int = 1
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    create_time: datetime = Field(default_factory=datetime.now)
    update_time: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})


class SysRole(SQLModel, table=True):
    __tablename__ = "sys_role"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    name: str
    sort_order: int = 0
    status: int = 1
    create_time: datetime = Field(default_factory=datetime.now)


class SysMenu(SQLModel, table=True):
    __tablename__ = "sys_menu"

    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: int = 0
    name: str
    path: str
    icon: Optional[str] = None
    sort_order: int = 0
    roles: str = "ADMIN"
    create_time: datetime = Field(default_factory=datetime.now)


class SysLoginLog(SQLModel, table=True):
    __tablename__ = "sys_login_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: Optional[str] = None
    ip: Optional[str] = None
    status: int = 1
    message: Optional[str] = None
    create_time: datetime = Field(default_factory=datetime.now)


class SysOperationLog(SQLModel, table=True):
    __tablename__ = "sys_operation_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: Optional[str] = None
    module: Optional[str] = None
    action: Optional[str] = None
    method: Optional[str] = None
    url: Optional[str] = None
    ip: Optional[str] = None
    cost_ms: Optional[int] = None
    status: int = 1
    create_time: datetime = Field(default_factory=datetime.now)


# 业务表（17 张）映射，见 models/travel.py（阶段 3）
from app.models.travel import *  # noqa: E402, F401
