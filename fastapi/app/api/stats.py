"""看板统计接口（见施工规范 §4.5 第 627 行、§7.7）。

前台 GET /api/stats/dashboard；管理端 GET /api/admin/stats（绝对路径，不叠 /stats 前缀，见避坑 24）。
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.common.result import Result
from app.core.deps import get_current_user, get_db, require_admin
from app.services import stats_service

router = APIRouter(prefix="/stats", tags=["看板统计"])
admin_router = APIRouter(prefix="/admin/stats", tags=["看板统计"])


@router.get("/dashboard")
def front_dashboard(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=stats_service.front_dashboard(db, current_user))


@admin_router.get("")
def admin_stats(current_user=Depends(require_admin), db: Session = Depends(get_db)):
    return Result(data=stats_service.admin_stats(db))
