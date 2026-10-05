"""个人中心接口（见施工规范 §4.8）。"""
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.common.result import Result
from app.core.deps import get_current_user, get_db
from app.schemas.profile import AvatarUpdateRequest, PasswordUpdateRequest, ProfileUpdateRequest
from app.services import profile_service

router = APIRouter(prefix="/profile", tags=["个人中心"])


@router.put("")
def update_profile(payload: ProfileUpdateRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=profile_service.update_profile(db, current_user, payload))


@router.put("/avatar")
def update_avatar(payload: AvatarUpdateRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=profile_service.update_avatar(db, current_user, payload.avatar))


@router.put("/password")
def update_password(payload: PasswordUpdateRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    profile_service.update_password(db, current_user, payload)
    return Result()
