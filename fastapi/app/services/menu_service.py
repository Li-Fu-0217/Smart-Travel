"""菜单服务（见施工规范 §4.5、§4.7）。"""
from typing import List

from sqlmodel import Session, select

from app.common.exceptions import BusinessException
from app.common.menu_paths import is_allowed_menu_path
from app.models import SysMenu
from app.schemas.menu import MenuCreateRequest, MenuUpdateRequest, MenuVO


def to_vo(menu: SysMenu) -> MenuVO:
    roles = [r for r in (menu.roles or "").split(",") if r]
    return MenuVO(
        id=menu.id,
        parent_id=menu.parent_id,
        name=menu.name,
        path=menu.path,
        icon=menu.icon,
        sort_order=menu.sort_order,
        roles=roles,
    )


def list_menus(db: Session, role: str = None) -> List[MenuVO]:
    menus = db.exec(select(SysMenu).order_by(SysMenu.sort_order)).all()
    if role:
        menus = [m for m in menus if role in (m.roles or "").split(",")]
    return [to_vo(m) for m in menus]


def create_menu(db: Session, payload: MenuCreateRequest) -> MenuVO:
    if not is_allowed_menu_path(payload.path):
        raise BusinessException("菜单路径不在白名单内", code=400)
    menu = SysMenu(
        parent_id=0,
        name=payload.name,
        path=payload.path,
        icon=payload.icon,
        sort_order=payload.sort_order,
        roles=",".join(payload.roles),
    )
    db.add(menu)
    db.commit()
    db.refresh(menu)
    return to_vo(menu)


def update_menu(db: Session, menu_id: int, payload: MenuUpdateRequest) -> MenuVO:
    menu = db.get(SysMenu, menu_id)
    if menu is None:
        raise BusinessException("菜单不存在", code=404)
    if not is_allowed_menu_path(payload.path):
        raise BusinessException("菜单路径不在白名单内", code=400)
    menu.name = payload.name
    menu.path = payload.path
    menu.icon = payload.icon
    menu.sort_order = payload.sort_order
    menu.roles = ",".join(payload.roles)
    db.add(menu)
    db.commit()
    db.refresh(menu)
    return to_vo(menu)


def delete_menu(db: Session, menu_id: int) -> None:
    menu = db.get(SysMenu, menu_id)
    if menu is None:
        raise BusinessException("菜单不存在", code=404)
    db.delete(menu)
    db.commit()


def batch_delete(db: Session, ids: List[int]) -> None:
    for mid in ids:
        menu = db.get(SysMenu, mid)
        if menu is not None:
            db.delete(menu)
    db.commit()
