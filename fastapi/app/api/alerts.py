"""旅途求助接口（见施工规范 §4.5、§5.8）。"""
from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session

from app.common.result import PageResult, Result
from app.core.deps import get_current_user, get_db, operation_log, require_admin
from app.schemas.alert import AlertCreateRequest, AlertUpdateRequest
from app.services import alert_service

router = APIRouter(prefix="/alerts", tags=["旅途求助"])
admin_router = APIRouter(prefix="/admin/alerts", tags=["旅途求助"])


@router.post("/sos")
@operation_log("旅途求助", "发起求助")
def sos(payload: AlertCreateRequest, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=alert_service.create_sos(db, current_user, payload))


@router.get("")
def list_alerts(
    current: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: str | None = Query(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records, total = alert_service.list_alerts(db, current_user, current, size, status)
    return Result(data=PageResult(records=records, total=total, current=current, size=size))


@admin_router.get("")
def admin_list_alerts(
    current: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: str | None = Query(None),
    keyword: str = Query(""),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    records, total = alert_service.admin_list_alerts(db, current, size, status, keyword)
    return Result(data=PageResult(records=records, total=total, current=current, size=size))


@admin_router.put("/{alert_id}")
@operation_log("旅途求助", "处理工单")
def admin_update_alert(alert_id: int, payload: AlertUpdateRequest, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    return Result(data=alert_service.admin_update_alert(db, alert_id, payload))
