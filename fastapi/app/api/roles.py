"""角色接口（见施工规范 §4.5，仅查询）。"""
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.common.result import Result
from app.core.deps import get_current_user, get_db
from app.services import role_service

router = APIRouter(prefix="/roles", tags=["角色"])


@router.get("")
def list_roles(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=role_service.list_roles(db))
