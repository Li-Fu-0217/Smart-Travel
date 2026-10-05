"""菜单出入参（见施工规范 §4.5）。"""
from typing import List, Optional

from pydantic import Field

from app.common.result import CamelModel


class MenuVO(CamelModel):
    id: int
    parent_id: int
    name: str
    path: str
    icon: Optional[str] = None
    sort_order: int
    roles: List[str]


class MenuCreateRequest(CamelModel):
    name: str = Field(..., max_length=50)
    path: str = Field(..., max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    sort_order: int = 0
    roles: List[str] = ["ADMIN"]


class MenuUpdateRequest(CamelModel):
    name: str = Field(..., max_length=50)
    path: str = Field(..., max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    sort_order: int = 0
    roles: List[str] = ["ADMIN"]
