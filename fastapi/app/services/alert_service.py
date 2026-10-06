"""旅途求助服务（见施工规范 §4.5、§5.8）。"""
import logging
from typing import List

from sqlmodel import Session, func, select

from app.common.exceptions import BusinessException
from app.models import FamilyMember, SysUser, TravelAlert, TravelerProfile
from app.schemas.alert import AlertCreateRequest, AlertUpdateRequest, AlertVO
from app.services import notification_service
from app.services.family_service import assert_family_access

logger = logging.getLogger(__name__)


def _bound_ids(db: Session, user: SysUser) -> List[int]:
    return db.exec(select(FamilyMember.traveler_id).where(FamilyMember.user_id == user.id)).all()


def to_vo(db: Session, a: TravelAlert) -> AlertVO:
    traveler = db.get(TravelerProfile, a.traveler_id)
    return AlertVO(
        id=a.id,
        traveler_id=a.traveler_id,
        traveler_name=traveler.name if traveler else None,
        location=a.location,
        message=a.message,
        alert_type=a.alert_type,
        status=a.status,
        notify_family=a.notify_family,
        notify_staff=a.notify_staff,
        source=a.source,
        create_time=a.create_time,
    )


def create_sos(db: Session, user: SysUser, payload: AlertCreateRequest) -> AlertVO:
    assert_family_access(db, user, payload.traveler_id)
    alert = TravelAlert(
        traveler_id=payload.traveler_id,
        location=payload.location,
        message=payload.message,
        alert_type=payload.alert_type,
        status="open",
        notify_family=payload.notify_family,
        notify_staff=payload.notify_staff,
        source=payload.source,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    # 通知推送（失败不影响 SOS 主流程，见 §9 阶段 3.6）
    try:
        _notify_sos(db, alert)
    except Exception:
        logger.exception("SOS 通知写入失败 alert_id=%s", alert.id)
    return to_vo(db, alert)


def list_alerts(db: Session, user: SysUser, current: int, size: int, status: str | None) -> tuple[List[AlertVO], int]:
    stmt = select(TravelAlert)
    count_stmt = select(func.count(TravelAlert.id))
    if user.role != "ADMIN":
        ids = _bound_ids(db, user)
        stmt = stmt.where(TravelAlert.traveler_id.in_(ids))
        count_stmt = count_stmt.where(TravelAlert.traveler_id.in_(ids))
    if status:
        stmt = stmt.where(TravelAlert.status == status)
        count_stmt = count_stmt.where(TravelAlert.status == status)
    total = db.exec(count_stmt).one()
    alerts = db.exec(stmt.order_by(TravelAlert.id.desc()).offset((current - 1) * size).limit(size)).all()
    return [to_vo(db, a) for a in alerts], total


def admin_list_alerts(db: Session, current: int, size: int, status: str | None) -> tuple[List[AlertVO], int]:
    stmt = select(TravelAlert)
    count_stmt = select(func.count(TravelAlert.id))
    if status:
        stmt = stmt.where(TravelAlert.status == status)
        count_stmt = count_stmt.where(TravelAlert.status == status)
    total = db.exec(count_stmt).one()
    alerts = db.exec(stmt.order_by(TravelAlert.id.desc()).offset((current - 1) * size).limit(size)).all()
    return [to_vo(db, a) for a in alerts], total


def admin_update_alert(db: Session, alert_id: int, payload: AlertUpdateRequest) -> AlertVO:
    alert = db.get(TravelAlert, alert_id)
    if alert is None:
        raise BusinessException("求助工单不存在", code=404)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(alert, field, value)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return to_vo(db, alert)


def _notify_sos(db: Session, alert: TravelAlert) -> None:
    """按 notify_family / notify_staff 写站内消息（§9 阶段 3.6）。"""
    if not alert.notify_family and not alert.notify_staff:
        return
    title = "旅途求助"
    content = alert.message or alert.location or "家人发起了求助"
    if alert.notify_family:
        uids = db.exec(select(FamilyMember.user_id).where(FamilyMember.traveler_id == alert.traveler_id)).all()
        for uid in uids:
            notification_service.push(db, uid, alert.traveler_id, title, content, "alert", alert.source, alert.id)
    if alert.notify_staff:
        admin_ids = db.exec(select(SysUser.id).where(SysUser.role == "ADMIN")).all()
        for uid in admin_ids:
            notification_service.push(db, uid, alert.traveler_id, title, content, "alert", alert.source, alert.id)
