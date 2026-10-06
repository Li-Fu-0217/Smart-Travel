"""行程模板接口（见施工规范 §4.5）。

登录级 /templates/*；管理级 /admin/templates/*（独立 router，避免前缀拼接错误）。
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session

from app.common.result import PageResult, Result
from app.core.deps import get_current_user, get_db, operation_log, require_admin
from app.schemas.template import TemplateCopyRequest, TemplatePublishRequest, TemplateUpdateRequest
from app.services import template_service

router = APIRouter(prefix="/templates", tags=["行程模板"])
admin_router = APIRouter(prefix="/admin/templates", tags=["行程模板"])


@router.get("")
def list_templates(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=template_service.list_templates(db))


@router.get("/{template_id}")
def get_template(template_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=template_service.get_template(db, template_id))


@router.post("")
@operation_log("行程模板", "发布模板")
def publish(payload: TemplatePublishRequest, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=template_service.publish(db, current_user, payload))


@router.post("/{template_id}/copy")
@operation_log("行程模板", "复制模板")
def copy_template(template_id: int, payload: TemplateCopyRequest, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=template_service.copy_template(db, current_user, template_id, payload))


@admin_router.get("")
def admin_list_templates(
    current: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: str = Query(""),
    day_range: str = Query("", alias="dayRange"),
    use_range: str = Query("", alias="useRange"),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    records, total = template_service.admin_list_templates(db, current, size, keyword, day_range, use_range)
    return Result(data=PageResult(records=records, total=total, current=current, size=size))


@admin_router.put("/{template_id}")
@operation_log("行程模板", "修改模板")
def admin_update_template(template_id: int, payload: TemplateUpdateRequest, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    return Result(data=template_service.admin_update_template(db, template_id, payload))


@admin_router.delete("/{template_id}")
@operation_log("行程模板", "删除模板")
def admin_delete_template(template_id: int, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    template_service.admin_delete_template(db, template_id)
    return Result()
