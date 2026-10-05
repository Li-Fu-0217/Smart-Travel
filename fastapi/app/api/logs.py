"""日志接口（见施工规范 §4.5，管理员）。"""
from typing import List

from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session

from app.common.exceptions import BusinessException
from app.common.result import PageResult, Result
from app.core.deps import get_db, operation_log, require_admin
from app.services import log_service

router = APIRouter(prefix="/logs", tags=["系统日志"])


@router.get("")
def list_logs(
    type: str = Query("login"),
    current: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    if type == "login":
        records, total = log_service.list_login_logs(db, current, size)
    elif type == "operation":
        records, total = log_service.list_operation_logs(db, current, size)
    else:
        raise BusinessException("日志类型不合法", code=400)
    return Result(data=PageResult(records=records, total=total, current=current, size=size))


@router.delete("/batch")
@operation_log("系统日志", "批量删除日志")
def batch_delete_logs(
    type: str = Query("login"),
    ids: List[int] = None,
    request: Request = None,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    if type == "login":
        log_service.batch_delete_login(db, ids or [])
    elif type == "operation":
        log_service.batch_delete_operation(db, ids or [])
    else:
        raise BusinessException("日志类型不合法", code=400)
    return Result()
