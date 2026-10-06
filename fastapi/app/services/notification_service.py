"""站内消息服务（见施工规范 §4.5、§9 阶段 3.6）。"""
import logging
from typing import List, Optional

from sqlmodel import Session, func, select

from app.common.exceptions import BusinessException
from app.models import FamilyMember, NotifyInbox, SysUser
from app.schemas.notification import NotificationVO

logger = logging.getLogger(__name__)


def to_vo(n: NotifyInbox) -> NotificationVO:
    return NotificationVO(
        id=n.id,
        user_id=n.user_id,
        traveler_id=n.traveler_id,
        title=n.title,
        content=n.content,
        msg_type=n.msg_type,
        source=n.source,
        related_id=n.related_id,
        is_read=n.is_read,
        create_time=n.create_time,
    )


def list_notifications(db: Session, user: SysUser, current: int, size: int) -> tuple[List[NotificationVO], int]:
    total = db.exec(select(func.count(NotifyInbox.id)).where(NotifyInbox.user_id == user.id)).one()
    rows = db.exec(
        select(NotifyInbox).where(NotifyInbox.user_id == user.id).order_by(NotifyInbox.id.desc()).offset((current - 1) * size).limit(size)
    ).all()
    return [to_vo(n) for n in rows], total


def unread_count(db: Session, user: SysUser) -> int:
    return db.exec(
        select(func.count(NotifyInbox.id)).where(NotifyInbox.user_id == user.id, NotifyInbox.is_read == 0)
    ).one()


def mark_read(db: Session, user: SysUser, notification_id: int) -> NotificationVO:
    n = db.get(NotifyInbox, notification_id)
    if n is None:
        raise BusinessException("消息不存在", code=404)
    if n.user_id != user.id:
        raise BusinessException("无权访问该消息", code=403)
    if n.is_read != 1:  # 幂等：已读不再写
        n.is_read = 1
        db.add(n)
        db.commit()
        db.refresh(n)
    return to_vo(n)


def mark_read_all(db: Session, user: SysUser) -> int:
    unread = db.exec(select(NotifyInbox).where(NotifyInbox.user_id == user.id, NotifyInbox.is_read == 0)).all()
    for n in unread:
        n.is_read = 1
        db.add(n)
    db.commit()
    return len(unread)


def push(
    db: Session,
    user_id: int,
    traveler_id: Optional[int],
    title: str,
    content: str,
    msg_type: str,
    source: str,
    related_id: Optional[int] = None,
) -> NotifyInbox:
    """写入一条站内消息（供 SOS 等业务调用，见 §9 阶段 3.6）。"""
    n = NotifyInbox(
        user_id=user_id,
        traveler_id=traveler_id,
        title=title,
        content=content,
        msg_type=msg_type,
        source=source,
        related_id=related_id,
        is_read=0,
    )
    db.add(n)
    db.commit()
    db.refresh(n)
    return n


def notify_companions(db: Session, traveler_id: int, content: str, source: str = "agent") -> dict:
    """向该旅行者的绑定联系人发送站内消息（§6.2 工具 5）。无绑定时通知数为 0。"""
    uids = db.exec(
        select(FamilyMember.user_id).where(FamilyMember.traveler_id == traveler_id)
    ).all()
    for uid in uids:
        push(db, uid, traveler_id, "同行人通知", content, "agent_notify", source)
    return {"notified_count": len(uids)}
