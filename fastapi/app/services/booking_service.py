"""预约服务（见施工规范 §4.5、§4.9、§5.7、§5.8）。

防超卖两层：uk_booking_slot_lock 唯一约束（下单/改约捕获 IntegrityError）+ version 乐观锁（改约）。
slot_lock 一律服务端计算，取消/完成置 NULL 释放时段。
"""
from datetime import date, datetime, timedelta
from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, func, select

from app.common.constants import SOURCES
from app.common.exceptions import BusinessException
from app.models import BookingCatalog, BookingOrder, FamilyMember, SysUser
from app.schemas.booking import (
    BookingCatalogCreateRequest,
    BookingCatalogUpdateRequest,
    BookingCatalogVO,
    BookingOrderCreateRequest,
    BookingOrderUpdateRequest,
    BookingOrderVO,
    BookingSlotVO,
)
from app.services.family_service import assert_family_access

_SLOT_TIMES = ("09:00", "14:00", "19:00")


def slot_lock_to_slot(slot_lock: Optional[str]) -> Optional[str]:
    """锁键 '目录ID:yyyyMMddHHmm' → 展示时段 'YYYY-MM-DD HH:MM'。"""
    if not slot_lock:
        return None
    _, compact = slot_lock.split(":", 1)
    return f"{compact[:4]}-{compact[4:6]}-{compact[6:8]} {compact[8:10]}:{compact[10:12]}"


def to_catalog_vo(c: BookingCatalog) -> BookingCatalogVO:
    return BookingCatalogVO(
        id=c.id,
        name=c.name,
        item_type=c.item_type,
        description=c.description,
        duration_minutes=c.duration_minutes,
        price=c.price,
        status=c.status,
        create_time=c.create_time,
    )


def to_order_vo(db: Session, o: BookingOrder) -> BookingOrderVO:
    catalog = db.get(BookingCatalog, o.catalog_id)
    return BookingOrderVO(
        id=o.id,
        traveler_id=o.traveler_id,
        catalog_id=o.catalog_id,
        catalog_name=catalog.name if catalog else None,
        booking_time=o.booking_time,
        guest_count=o.guest_count,
        status=o.status,
        source=o.source,
        slot=slot_lock_to_slot(o.slot_lock),
        version=o.version,
        remark=o.remark,
        create_time=o.create_time,
        update_time=o.update_time,
    )


def _bound_ids(db: Session, user: SysUser) -> List[int]:
    return db.exec(select(FamilyMember.traveler_id).where(FamilyMember.user_id == user.id)).all()


def _validate_slot(slot: str) -> datetime:
    try:
        dt = datetime.strptime(slot, "%Y-%m-%d %H:%M")
    except ValueError:
        raise BusinessException("时段格式不合法", code=400)
    if dt.strftime("%H:%M") not in _SLOT_TIMES:
        raise BusinessException("时段不合法", code=400)
    return dt


# —— catalog ——

def list_catalog(db: Session, user: SysUser) -> List[BookingCatalogVO]:
    catalogs = db.exec(
        select(BookingCatalog).where(BookingCatalog.status == 1).order_by(BookingCatalog.id)
    ).all()
    return [to_catalog_vo(c) for c in catalogs]


def admin_list_catalog(db: Session, current: int, size: int, keyword: str) -> tuple[List[BookingCatalogVO], int]:
    stmt = select(BookingCatalog)
    count_stmt = select(func.count(BookingCatalog.id))
    if keyword:
        cond = BookingCatalog.name.contains(keyword) | BookingCatalog.description.contains(keyword)
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)
    total = db.exec(count_stmt).one()
    catalogs = db.exec(stmt.order_by(BookingCatalog.id).offset((current - 1) * size).limit(size)).all()
    return [to_catalog_vo(c) for c in catalogs], total


def admin_create_catalog(db: Session, payload: BookingCatalogCreateRequest) -> BookingCatalogVO:
    catalog = BookingCatalog(
        name=payload.name,
        item_type=payload.item_type,
        description=payload.description,
        duration_minutes=payload.duration_minutes,
        price=payload.price,
        status=payload.status,
    )
    db.add(catalog)
    db.commit()
    db.refresh(catalog)
    return to_catalog_vo(catalog)


def admin_update_catalog(db: Session, catalog_id: int, payload: BookingCatalogUpdateRequest) -> BookingCatalogVO:
    catalog = db.get(BookingCatalog, catalog_id)
    if catalog is None:
        raise BusinessException("预约项目不存在", code=404)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(catalog, field, value)
    db.add(catalog)
    db.commit()
    db.refresh(catalog)
    return to_catalog_vo(catalog)


def admin_delete_catalog(db: Session, catalog_id: int) -> None:
    catalog = db.get(BookingCatalog, catalog_id)
    if catalog is None:
        raise BusinessException("预约项目不存在", code=404)
    db.delete(catalog)
    db.commit()


# —— slots ——

def slots(db: Session, item_type: Optional[str], days: int) -> List[BookingSlotVO]:
    days = max(1, min(days, 30))
    stmt = select(BookingCatalog).where(BookingCatalog.status == 1)
    if item_type:
        stmt = stmt.where(BookingCatalog.item_type == item_type)
    catalogs = db.exec(stmt.order_by(BookingCatalog.id)).all()

    occupied = set(db.exec(
        select(BookingOrder.slot_lock).where(
            BookingOrder.status.in_(("pending", "confirmed")),
            BookingOrder.slot_lock.is_not(None),
        )
    ).all())

    today = date.today()
    result: List[BookingSlotVO] = []
    for c in catalogs:
        free: List[str] = []
        for d in range(days):
            day = today + timedelta(days=d)
            for hm in _SLOT_TIMES:
                slot_str = f"{day.strftime('%Y-%m-%d')} {hm}"
                lock = f"{c.id}:{day.strftime('%Y%m%d')}{hm.replace(':', '')}"
                if lock not in occupied:
                    free.append(slot_str)
        result.append(BookingSlotVO(
            catalog_id=c.id,
            catalog_name=c.name,
            item_type=c.item_type,
            duration_minutes=c.duration_minutes,
            price=c.price,
            slots=free,
        ))
    return result


# —— orders ——

def create_order(db: Session, user: SysUser, payload: BookingOrderCreateRequest, source: str = "manual") -> BookingOrderVO:
    # source 值域 §5.8：manual（人工）/ agent（智能助手）/ system（系统）。默认 manual 保持人工下单现行为。
    if source not in SOURCES:
        raise BusinessException("来源不合法", code=400)
    assert_family_access(db, user, payload.traveler_id)
    catalog = db.get(BookingCatalog, payload.catalog_id)
    if catalog is None or catalog.status != 1:
        raise BusinessException("预约项目不存在或已下架", code=404)
    dt = _validate_slot(payload.slot)
    slot_lock = f"{catalog.id}:{dt.strftime('%Y%m%d%H%M')}"
    order = BookingOrder(
        traveler_id=payload.traveler_id,
        catalog_id=catalog.id,
        booking_time=datetime.now(),
        guest_count=payload.guest_count,
        status="pending",
        source=source,
        slot_lock=slot_lock,
        version=0,
        remark=payload.remark,
    )
    db.add(order)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise BusinessException("该时段已被预约", code=400)
    db.refresh(order)
    return to_order_vo(db, order)


def list_orders(db: Session, user: SysUser, current: int, size: int, status: Optional[str]) -> tuple[List[BookingOrderVO], int]:
    stmt = select(BookingOrder)
    count_stmt = select(func.count(BookingOrder.id))
    if user.role != "ADMIN":
        ids = _bound_ids(db, user)
        stmt = stmt.where(BookingOrder.traveler_id.in_(ids))
        count_stmt = count_stmt.where(BookingOrder.traveler_id.in_(ids))
    if status:
        stmt = stmt.where(BookingOrder.status == status)
        count_stmt = count_stmt.where(BookingOrder.status == status)
    total = db.exec(count_stmt).one()
    orders = db.exec(stmt.order_by(BookingOrder.id.desc()).offset((current - 1) * size).limit(size)).all()
    return [to_order_vo(db, o) for o in orders], total


def get_order(db: Session, user: SysUser, order_id: int) -> BookingOrderVO:
    order = db.get(BookingOrder, order_id)
    if order is None:
        raise BusinessException("预约订单不存在", code=404)
    assert_family_access(db, user, order.traveler_id)
    return to_order_vo(db, order)


def cancel_order(db: Session, user: SysUser, order_id: int) -> BookingOrderVO:
    order = db.get(BookingOrder, order_id)
    if order is None:
        raise BusinessException("预约订单不存在", code=404)
    assert_family_access(db, user, order.traveler_id)
    order.status = "cancelled"
    order.slot_lock = None
    db.add(order)
    db.commit()
    db.refresh(order)
    return to_order_vo(db, order)


def admin_list_orders(db: Session, current: int, size: int, status: Optional[str]) -> tuple[List[BookingOrderVO], int]:
    stmt = select(BookingOrder)
    count_stmt = select(func.count(BookingOrder.id))
    if status:
        stmt = stmt.where(BookingOrder.status == status)
        count_stmt = count_stmt.where(BookingOrder.status == status)
    total = db.exec(count_stmt).one()
    orders = db.exec(stmt.order_by(BookingOrder.id.desc()).offset((current - 1) * size).limit(size)).all()
    return [to_order_vo(db, o) for o in orders], total


def admin_update_order(db: Session, order_id: int, payload: BookingOrderUpdateRequest) -> BookingOrderVO:
    order = db.get(BookingOrder, order_id)
    if order is None:
        raise BusinessException("预约订单不存在", code=404)
    if payload.version != order.version:
        raise BusinessException("该预约刚被他人修改，请刷新后重试", code=400)

    new_slot_lock = order.slot_lock
    if payload.status in ("cancelled", "done"):
        new_slot_lock = None
    elif payload.slot:
        dt = _validate_slot(payload.slot)
        new_slot_lock = f"{order.catalog_id}:{dt.strftime('%Y%m%d%H%M')}"

    if payload.status is not None:
        order.status = payload.status
    if payload.remark is not None:
        order.remark = payload.remark
    order.slot_lock = new_slot_lock
    order.version = order.version + 1
    db.add(order)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise BusinessException("该时段已被预约", code=400)
    db.refresh(order)
    return to_order_vo(db, order)
