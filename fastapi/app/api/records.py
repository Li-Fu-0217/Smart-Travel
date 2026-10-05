"""旅游记录接口（见施工规范 §4.5、§5.8）。"""
from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session

from app.common.result import PageResult, Result
from app.core.deps import get_current_user, get_db, operation_log, require_admin
from app.schemas.record import RecordCreateRequest, RecordUpdateRequest
from app.services import record_service

router = APIRouter(prefix="/records", tags=["旅游记录"])
admin_router = APIRouter(prefix="/admin/records", tags=["旅游记录"])


@router.get("")
def list_records(
    current: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records, total = record_service.list_records(db, current_user, current, size)
    return Result(data=PageResult(records=records, total=total, current=current, size=size))


@router.post("")
@operation_log("旅游记录", "新增记录")
def create_record(payload: RecordCreateRequest, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=record_service.create_record(db, current_user, payload))


@router.put("/{record_id}")
@operation_log("旅游记录", "修改记录")
def update_record(record_id: int, payload: RecordUpdateRequest, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=record_service.update_record(db, current_user, record_id, payload))


@router.delete("/{record_id}")
@operation_log("旅游记录", "删除记录")
def delete_record(record_id: int, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    record_service.delete_record(db, current_user, record_id)
    return Result()


@admin_router.get("")
def admin_list_records(
    current: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    traveler_id: int | None = Query(None, alias="travelerId"),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    records, total = record_service.admin_list_records(db, current, size, traveler_id)
    return Result(data=PageResult(records=records, total=total, current=current, size=size))
