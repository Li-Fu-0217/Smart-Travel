"""菜单接口（见施工规范 §4.5）。"""
from typing import List

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.common.result import Result
from app.core.deps import get_current_user, get_db, operation_log, require_admin
from app.schemas.menu import MenuCreateRequest, MenuUpdateRequest
from app.services import menu_service

router = APIRouter(prefix="/menus", tags=["菜单"])


@router.get("")
def list_menus(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=menu_service.list_menus(db, current_user.role))


@router.get("/manage")
def list_manage(current_user=Depends(require_admin), db: Session = Depends(get_db)):
    return Result(data=menu_service.list_menus(db))


@router.post("")
@operation_log("菜单管理", "创建菜单")
def create_menu(payload: MenuCreateRequest, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    return Result(data=menu_service.create_menu(db, payload))


@router.put("/{menu_id}")
@operation_log("菜单管理", "修改菜单")
def update_menu(menu_id: int, payload: MenuUpdateRequest, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    return Result(data=menu_service.update_menu(db, menu_id, payload))


@router.delete("/{menu_id}")
@operation_log("菜单管理", "删除菜单")
def delete_menu(menu_id: int, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    menu_service.delete_menu(db, menu_id)
    return Result()


@router.delete("/batch")
@operation_log("菜单管理", "批量删除菜单")
def batch_delete(ids: List[int], request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    menu_service.batch_delete(db, ids)
    return Result()
