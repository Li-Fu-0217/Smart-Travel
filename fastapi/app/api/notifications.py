"""站内消息接口（见施工规范 §4.5、§9 阶段 3.6）。

全部登录级，只读写当前用户自己的消息，无 admin 变体。
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session

from app.common.result import PageResult, Result
from app.core.deps import get_current_user, get_db, operation_log
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["站内消息"])


@router.get("")
def list_notifications(
    current: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records, total = notification_service.list_notifications(db, current_user, current, size)
    return Result(data=PageResult(records=records, total=total, current=current, size=size))


@router.get("/unread-count")
def unread_count(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=notification_service.unread_count(db, current_user))


@router.put("/{notification_id}/read")
@operation_log("站内消息", "标记已读")
def mark_read(notification_id: int, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=notification_service.mark_read(db, current_user, notification_id))


@router.put("/read-all")
@operation_log("站内消息", "全部已读")
def mark_read_all(request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=notification_service.mark_read_all(db, current_user))
