"""拼团活动接口（见施工规范 §4.5、§5.8、避坑 27）。

登录级 /tours/*；管理级 /admin/tours/*（独立 router，避免前缀拼接错误）。
注意：/tours/my-signups 为固定路径，若未来加 GET /tours/{id}，必须先于其声明（避坑 25）。
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session

from app.common.result import PageResult, Result
from app.core.deps import get_current_user, get_db, operation_log, require_admin
from app.schemas.tour import SignupRequest, TourCreateRequest, TourUpdateRequest
from app.services import tour_service

router = APIRouter(prefix="/tours", tags=["拼团活动"])
admin_router = APIRouter(prefix="/admin/tours", tags=["拼团活动"])


@router.get("/my-signups")
def my_signups(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=tour_service.my_signups(db, current_user))


@router.get("")
def list_tours(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=tour_service.list_tours(db))


@router.post("/{tour_id}/signup")
@operation_log("拼团活动", "报名")
def signup(tour_id: int, payload: SignupRequest, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=tour_service.signup(db, current_user, tour_id, payload.traveler_id))


@admin_router.get("/signups")
def admin_list_signups(
    current: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    tour_id: int | None = Query(None, alias="tourId"),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    records, total = tour_service.admin_list_signups(db, current, size, tour_id)
    return Result(data=PageResult(records=records, total=total, current=current, size=size))


@admin_router.get("")
def admin_list_tours(
    current: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: str = Query(""),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    records, total = tour_service.admin_list_tours(db, current, size, keyword)
    return Result(data=PageResult(records=records, total=total, current=current, size=size))


@admin_router.post("")
@operation_log("拼团活动", "创建活动")
def admin_create_tour(payload: TourCreateRequest, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    return Result(data=tour_service.admin_create_tour(db, payload))


@admin_router.put("/{tour_id}")
@operation_log("拼团活动", "修改活动")
def admin_update_tour(tour_id: int, payload: TourUpdateRequest, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    return Result(data=tour_service.admin_update_tour(db, tour_id, payload))


@admin_router.delete("/{tour_id}")
@operation_log("拼团活动", "删除活动")
def admin_delete_tour(tour_id: int, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    tour_service.admin_delete_tour(db, tour_id)
    return Result()
