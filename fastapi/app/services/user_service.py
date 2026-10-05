"""用户服务（见施工规范 §4.1、§4.5）。"""
from typing import List

from sqlmodel import Session, func, select

from app.common.exceptions import BusinessException
from app.core.security import create_access_token, hash_password, verify_password
from app.models import SysLoginLog, SysUser
from app.schemas.auth import UserVO
from app.schemas.user import UserCreateRequest, UserUpdateRequest


def to_vo(user: SysUser) -> UserVO:
    return UserVO(
        id=user.id,
        username=user.username,
        role=user.role,
        status=user.status,
        nickname=user.nickname,
        email=user.email,
        phone=user.phone,
        avatar=user.avatar,
        create_time=user.create_time,
        update_time=user.update_time,
    )


def register(db: Session, username: str, password: str) -> UserVO:
    existing = db.exec(select(SysUser).where(SysUser.username == username)).first()
    if existing is not None:
        raise BusinessException("用户名已存在", code=400)
    user = SysUser(username=username, password=hash_password(password), role="USER", status=1)
    db.add(user)
    db.commit()
    db.refresh(user)
    return to_vo(user)


def login(db: Session, username: str, password: str, ip: str) -> tuple[str, UserVO]:
    user = db.exec(select(SysUser).where(SysUser.username == username)).first()
    if user is None or not verify_password(password, user.password):
        _write_login_log(db, username, ip, 0, "用户名或密码错误")
        raise BusinessException("用户名或密码错误", code=401)
    if user.status != 1:
        _write_login_log(db, username, ip, 0, "账号已被禁用")
        raise BusinessException("账号已被禁用", code=401)
    _write_login_log(db, username, ip, 1, "登录成功")
    return create_access_token(user.username), to_vo(user)


def list_users(db: Session, current: int, size: int, keyword: str) -> tuple[List[UserVO], int]:
    stmt = select(SysUser)
    count_stmt = select(func.count(SysUser.id))
    if keyword:
        cond = SysUser.username.contains(keyword)
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)
    total = db.exec(count_stmt).one()
    users = db.exec(stmt.order_by(SysUser.id).offset((current - 1) * size).limit(size)).all()
    return [to_vo(u) for u in users], total


def get_user(db: Session, user_id: int) -> UserVO:
    user = db.get(SysUser, user_id)
    if user is None:
        raise BusinessException("用户不存在", code=404)
    return to_vo(user)


def create_user(db: Session, payload: UserCreateRequest) -> UserVO:
    existing = db.exec(select(SysUser).where(SysUser.username == payload.username)).first()
    if existing is not None:
        raise BusinessException("用户名已存在", code=400)
    user = SysUser(username=payload.username, password=hash_password(payload.password),
                   role=payload.role, status=payload.status)
    db.add(user)
    db.commit()
    db.refresh(user)
    return to_vo(user)


def update_user(db: Session, user_id: int, payload: UserUpdateRequest) -> UserVO:
    user = db.get(SysUser, user_id)
    if user is None:
        raise BusinessException("用户不存在", code=404)
    user.role = payload.role
    user.status = payload.status
    db.add(user)
    db.commit()
    db.refresh(user)
    return to_vo(user)


def delete_user(db: Session, user_id: int) -> None:
    user = db.get(SysUser, user_id)
    if user is None:
        raise BusinessException("用户不存在", code=404)
    db.delete(user)
    db.commit()


def batch_delete(db: Session, ids: List[int]) -> None:
    for uid in ids:
        user = db.get(SysUser, uid)
        if user is not None:
            db.delete(user)
    db.commit()


def _write_login_log(db: Session, username: str, ip: str, status: int, message: str) -> None:
    db.add(SysLoginLog(username=username, ip=ip, status=status, message=message))
    db.commit()
