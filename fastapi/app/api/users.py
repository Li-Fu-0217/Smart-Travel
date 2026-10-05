"""用户接口（见施工规范 §4.5，管理员）。"""
from typing import List

from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session

from app.common.result import PageResult, Result
from app.core.deps import get_db, operation_log, require_admin
from app.schemas.user import UserCreateRequest, UserUpdateRequest
from app.services import user_service

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("")
def list_users(
    current: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: str = Query(""),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    records, total = user_service.list_users(db, current, size, keyword)
    return Result(data=PageResult(records=records, total=total, current=current, size=size))


@router.get("/{user_id}")
def get_user(user_id: int, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    return Result(data=user_service.get_user(db, user_id))


@router.post("")
@operation_log("用户管理", "创建用户")
def create_user(payload: UserCreateRequest, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    return Result(data=user_service.create_user(db, payload))


@router.put("/{user_id}")
@operation_log("用户管理", "修改用户")
def update_user(user_id: int, payload: UserUpdateRequest, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    return Result(data=user_service.update_user(db, user_id, payload))


@router.delete("/{user_id}")
@operation_log("用户管理", "删除用户")
def delete_user(user_id: int, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    user_service.delete_user(db, user_id)
    return Result()


@router.delete("/batch")
@operation_log("用户管理", "批量删除用户")
def batch_delete(ids: List[int], request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    user_service.batch_delete(db, ids)
    return Result()
