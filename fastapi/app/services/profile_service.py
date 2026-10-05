"""个人中心服务（见施工规范 §4.8）。"""
from sqlmodel import Session

from app.common.exceptions import BusinessException
from app.core.security import hash_password, verify_password
from app.models import SysUser
from app.schemas.auth import UserVO
from app.schemas.profile import PasswordUpdateRequest, ProfileUpdateRequest
from app.services.user_service import to_vo


def update_profile(db: Session, user: SysUser, payload: ProfileUpdateRequest) -> UserVO:
    fields = payload.model_fields_set
    if "nickname" in fields:
        user.nickname = payload.nickname
    if "email" in fields:
        user.email = payload.email
    if "phone" in fields:
        user.phone = payload.phone
    db.add(user)
    db.commit()
    db.refresh(user)
    return to_vo(user)


def update_avatar(db: Session, user: SysUser, avatar: str) -> UserVO:
    user.avatar = avatar
    db.add(user)
    db.commit()
    db.refresh(user)
    return to_vo(user)


def update_password(db: Session, user: SysUser, payload: PasswordUpdateRequest) -> None:
    if not verify_password(payload.old_password, user.password):
        raise BusinessException("旧密码错误", code=400)
    user.password = hash_password(payload.new_password)
    db.add(user)
    db.commit()
