"""行程接口（见施工规范 §4.5、§4.11）。

注意路由顺序：/trips/today 必须注册在 /trips/{trip_id} 之前，
否则 "today" 会被 {trip_id} 捕获并按 int 解析导致 422（避坑清单第 25 条）。
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session

from app.common.result import PageResult, Result
from app.core.deps import get_current_user, get_db, operation_log
from app.schemas.trip import TripCreateRequest, TripUpdateRequest
from app.services import todo_service, trip_service

router = APIRouter(prefix="/trips", tags=["行程管理"])


@router.get("")
def list_trips(
    current: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: str = Query(""),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records, total = trip_service.list_trips(db, current_user, current, size, keyword)
    return Result(data=PageResult(records=records, total=total, current=current, size=size))


@router.get("/today")
def today(traveler_id: int = Query(..., alias="travelerId"), current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=trip_service.today(db, current_user, traveler_id))


@router.get("/{trip_id}")
def get_trip(trip_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=trip_service.get_trip(db, current_user, trip_id))


@router.get("/{trip_id}/todos")
def list_trip_todos(trip_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=todo_service.list_todos(db, current_user, trip_id))


@router.post("")
@operation_log("行程管理", "创建行程")
def create_trip(payload: TripCreateRequest, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=trip_service.create_trip(db, current_user, payload))


@router.put("/{trip_id}")
@operation_log("行程管理", "修改行程")
def update_trip(trip_id: int, payload: TripUpdateRequest, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=trip_service.update_trip(db, current_user, trip_id, payload))


@router.delete("/{trip_id}")
@operation_log("行程管理", "删除行程")
def delete_trip(trip_id: int, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    trip_service.delete_trip(db, current_user, trip_id)
    return Result()
