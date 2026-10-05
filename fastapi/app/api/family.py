"""家庭绑定接口（见施工规范 §4.5、§4.10）。

登录级端点挂 /family/*；管理级端点挂 /admin/family/*（独立 router，
避免被拼成 /family/admin/family 的错误路径）。
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session

from app.common.result import PageResult, Result
from app.core.deps import get_current_user, get_db, operation_log, require_admin
from app.schemas.family import FamilyAdminBindRequest, FamilyBindRequest
from app.services import family_service, traveler_service

router = APIRouter(prefix="/family", tags=["家庭绑定"])
admin_router = APIRouter(prefix="/admin/family", tags=["家庭绑定"])


@router.get("/my-travelers")
def my_travelers(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=traveler_service.list_my_travelers(db, current_user))


@router.get("/bindings")
def bindings(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=family_service.list_bindings(db, current_user))


@router.post("/bind")
@operation_log("家庭绑定", "绑定旅行者")
def bind(payload: FamilyBindRequest, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=family_service.bind(db, current_user, payload.name, payload.phone, payload.relation, payload.is_primary))


@router.delete("/bindings/{binding_id}")
@operation_log("家庭绑定", "解绑旅行者")
def unbind(binding_id: int, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    family_service.unbind(db, current_user, binding_id)
    return Result()


@admin_router.get("")
def admin_list(
    current: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: str = Query(""),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    records, total = family_service.admin_list_family(db, current, size, keyword)
    return Result(data=PageResult(records=records, total=total, current=current, size=size))


@admin_router.post("")
@operation_log("家庭绑定", "管理员绑定")
def admin_bind(payload: FamilyAdminBindRequest, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    return Result(data=family_service.admin_bind(db, payload.user_id, payload.traveler_id, payload.relation, payload.is_primary))


@admin_router.delete("/{binding_id}")
@operation_log("家庭绑定", "管理员解绑")
def admin_unbind(binding_id: int, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    family_service.admin_unbind(db, binding_id)
    return Result()
