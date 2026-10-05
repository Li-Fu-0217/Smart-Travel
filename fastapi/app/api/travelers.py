"""旅行者档案接口（见施工规范 §4.5，登录级，数据隔离）。"""
from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session

from app.common.result import PageResult, Result
from app.core.deps import get_current_user, get_db, operation_log
from app.schemas.traveler import TravelerCreateRequest, TravelerUpdateRequest
from app.services import traveler_service

router = APIRouter(prefix="/travelers", tags=["旅行者档案"])


@router.get("")
def list_travelers(
    current: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: str = Query(""),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records, total = traveler_service.list_travelers(db, current_user, current, size, keyword)
    return Result(data=PageResult(records=records, total=total, current=current, size=size))


@router.get("/{traveler_id}/profile")
def get_profile(traveler_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=traveler_service.get_profile(db, current_user, traveler_id))


@router.get("/{traveler_id}")
def get_traveler(traveler_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=traveler_service.get_traveler(db, current_user, traveler_id))


@router.post("")
@operation_log("旅行者档案", "创建旅行者")
def create_traveler(payload: TravelerCreateRequest, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=traveler_service.create_traveler(db, current_user, payload))


@router.put("/{traveler_id}")
@operation_log("旅行者档案", "修改旅行者")
def update_traveler(traveler_id: int, payload: TravelerUpdateRequest, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=traveler_service.update_traveler(db, current_user, traveler_id, payload))


@router.delete("/{traveler_id}")
@operation_log("旅行者档案", "删除旅行者")
def delete_traveler(traveler_id: int, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    traveler_service.delete_traveler(db, current_user, traveler_id)
    return Result()
