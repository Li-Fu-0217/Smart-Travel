"""角色服务（见施工规范 §4.5，仅查询）。"""
from typing import List

from sqlmodel import Session, select

from app.models import SysRole
from app.schemas.role import RoleVO


def list_roles(db: Session) -> List[RoleVO]:
    roles = db.exec(select(SysRole).order_by(SysRole.sort_order)).all()
    return [
        RoleVO(id=r.id, code=r.code, name=r.name, sort_order=r.sort_order, status=r.status)
        for r in roles
    ]
