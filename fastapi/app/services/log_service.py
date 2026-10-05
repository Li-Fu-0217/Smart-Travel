"""日志服务（见施工规范 §4.5）。"""
from typing import List

from sqlmodel import Session, func, select

from app.models import SysLoginLog, SysOperationLog
from app.schemas.log import LoginLogVO, OperationLogVO


def list_login_logs(db: Session, current: int, size: int) -> tuple[List[LoginLogVO], int]:
    total = db.exec(select(func.count(SysLoginLog.id))).one()
    rows = db.exec(
        select(SysLoginLog).order_by(SysLoginLog.id.desc()).offset((current - 1) * size).limit(size)
    ).all()
    vos = [
        LoginLogVO(id=r.id, username=r.username, ip=r.ip, status=r.status,
                   message=r.message, create_time=r.create_time)
        for r in rows
    ]
    return vos, total


def list_operation_logs(db: Session, current: int, size: int) -> tuple[List[OperationLogVO], int]:
    total = db.exec(select(func.count(SysOperationLog.id))).one()
    rows = db.exec(
        select(SysOperationLog).order_by(SysOperationLog.id.desc()).offset((current - 1) * size).limit(size)
    ).all()
    vos = [
        OperationLogVO(id=r.id, username=r.username, module=r.module, action=r.action,
                       method=r.method, url=r.url, ip=r.ip, cost_ms=r.cost_ms,
                       status=r.status, create_time=r.create_time)
        for r in rows
    ]
    return vos, total


def batch_delete_login(db: Session, ids: List[int]) -> None:
    for lid in ids:
        row = db.get(SysLoginLog, lid)
        if row is not None:
            db.delete(row)
    db.commit()


def batch_delete_operation(db: Session, ids: List[int]) -> None:
    for lid in ids:
        row = db.get(SysOperationLog, lid)
        if row is not None:
            db.delete(row)
    db.commit()
