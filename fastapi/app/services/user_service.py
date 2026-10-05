"""用户服务（见施工规范 §4.1、§4.5）。"""
from sqlmodel import Session, select

from app.common.exceptions import BusinessException
from app.core.security import create_access_token, hash_password, verify_password
from app.models import SysLoginLog, SysUser
from app.schemas.auth import UserVO


def to_vo(user: SysUser) -> UserVO:
    return UserVO(
        id=user.id,
        username=user.username,
        role=user.role,
        status=user.status,
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


def _write_login_log(db: Session, username: str, ip: str, status: int, message: str) -> None:
    db.add(SysLoginLog(username=username, ip=ip, status=status, message=message))
    db.commit()
