"""依赖注入（见施工规范 §4.3）。"""
import inspect
import time
from functools import wraps
from typing import Optional

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.common.exceptions import BusinessException
from app.common.web_utils import client_ip
from app.core.security import parse_username_from_token
from app.db.session import engine
from app.models import SysOperationLog, SysUser

_bearer = HTTPBearer(auto_error=False)


def get_db():
    """生成器依赖：每请求一个 Session，用完关闭。"""
    with Session(engine) as session:
        yield session


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: Session = Depends(get_db),
) -> SysUser:
    if credentials is None:
        raise BusinessException("未登录或登录已过期", code=401)
    username = parse_username_from_token(credentials.credentials)
    if username is None:
        raise BusinessException("未登录或登录已过期", code=401)
    user = db.exec(select(SysUser).where(SysUser.username == username)).first()
    if user is None or user.status != 1:
        raise BusinessException("账号不存在或已被禁用", code=401)
    return user


def require_admin(current_user: SysUser = Depends(get_current_user)) -> SysUser:
    if current_user.role != "ADMIN":
        raise BusinessException("无权限访问", code=403)
    return current_user


def operation_log(module: str, action: str):
    """装饰器：在 finally 中把操作写入 sys_operation_log。被装饰路由需注入 request 与 db。
    同时支持同步 def 与异步 async def 路由（见 §4.3）。"""

    def decorator(func):
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                request = kwargs.get("request")
                db = kwargs.get("db")
                start = time.perf_counter()
                status = 1
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    status = 0
                    raise
                finally:
                    if request is not None and db is not None:
                        _write_operation_log(db, request, module, action, start, status)

            return async_wrapper

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            request = kwargs.get("request")
            db = kwargs.get("db")
            start = time.perf_counter()
            status = 1
            try:
                return func(*args, **kwargs)
            except Exception:
                status = 0
                raise
            finally:
                if request is not None and db is not None:
                    _write_operation_log(db, request, module, action, start, status)

        return sync_wrapper

    return decorator


def _write_operation_log(db, request, module, action, start, status):
    try:
        username = None
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            username = parse_username_from_token(auth[7:])
        cost_ms = int((time.perf_counter() - start) * 1000)
        db.add(SysOperationLog(
            username=username,
            module=module,
            action=action,
            method=request.method,
            url=str(request.url.path),
            ip=client_ip(request),
            cost_ms=cost_ms,
            status=status,
        ))
        db.commit()
    except Exception:
        db.rollback()
