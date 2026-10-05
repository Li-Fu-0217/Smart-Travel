"""角色出入参（见施工规范 §4.5）。"""
from app.common.result import CamelModel


class RoleVO(CamelModel):
    id: int
    code: str
    name: str
    sort_order: int
    status: int
