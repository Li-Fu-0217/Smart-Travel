"""预约域接口（见施工规范 §4.5、§4.9）。

登录级端点挂 /booking/*；管理级端点挂 /admin/booking/*（独立 router，
避免被拼成 /booking/admin/booking/* 的错误路径，见 §4.10 路径陷阱记录）。
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session

from app.common.result import PageResult, Result
from app.core.deps import get_current_user, get_db, operation_log, require_admin
from app.schemas.booking import (
    BookingCatalogCreateRequest,
    BookingCatalogUpdateRequest,
    BookingOrderCreateRequest,
    BookingOrderUpdateRequest,
)
from app.services import booking_service

router = APIRouter(prefix="/booking", tags=["预约管理"])
admin_router = APIRouter(prefix="/admin/booking", tags=["预约管理"])


# —— 登录级 ——

@router.get("/catalog")
def list_catalog(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=booking_service.list_catalog(db, current_user))


@router.get("/slots")
def slots(
    item_type: str | None = Query(None, alias="itemType"),
    days: int = Query(7),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return Result(data=booking_service.slots(db, item_type, days))


@router.post("/orders")
@operation_log("预约管理", "创建预约")
def create_order(payload: BookingOrderCreateRequest, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=booking_service.create_order(db, current_user, payload))


@router.get("/orders")
def list_orders(
    current: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: str | None = Query(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records, total = booking_service.list_orders(db, current_user, current, size, status)
    return Result(data=PageResult(records=records, total=total, current=current, size=size))


@router.get("/orders/{order_id}")
def get_order(order_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=booking_service.get_order(db, current_user, order_id))


@router.post("/orders/{order_id}/cancel")
@operation_log("预约管理", "取消预约")
def cancel_order(order_id: int, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=booking_service.cancel_order(db, current_user, order_id))


# —— 管理级 ——

@admin_router.get("/catalog")
def admin_list_catalog(
    current: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: str = Query(""),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    records, total = booking_service.admin_list_catalog(db, current, size, keyword)
    return Result(data=PageResult(records=records, total=total, current=current, size=size))


@admin_router.post("/catalog")
@operation_log("预约管理", "创建预约项目")
def admin_create_catalog(payload: BookingCatalogCreateRequest, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    return Result(data=booking_service.admin_create_catalog(db, payload))


@admin_router.put("/catalog/{catalog_id}")
@operation_log("预约管理", "修改预约项目")
def admin_update_catalog(catalog_id: int, payload: BookingCatalogUpdateRequest, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    return Result(data=booking_service.admin_update_catalog(db, catalog_id, payload))


@admin_router.delete("/catalog/{catalog_id}")
@operation_log("预约管理", "删除预约项目")
def admin_delete_catalog(catalog_id: int, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    booking_service.admin_delete_catalog(db, catalog_id)
    return Result()


@admin_router.get("/orders")
def admin_list_orders(
    current: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: str | None = Query(None),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    records, total = booking_service.admin_list_orders(db, current, size, status)
    return Result(data=PageResult(records=records, total=total, current=current, size=size))


@admin_router.put("/orders/{order_id}")
@operation_log("预约管理", "改约/改状态")
def admin_update_order(order_id: int, payload: BookingOrderUpdateRequest, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    return Result(data=booking_service.admin_update_order(db, order_id, payload))
