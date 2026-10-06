"""旅游记录服务（见施工规范 §4.5、§5.8）。"""
from datetime import date
from typing import List

from sqlmodel import Session, func, select

from app.common.exceptions import BusinessException
from app.models import FamilyMember, SysUser, TravelRecord, TravelerProfile
from app.schemas.record import RecordCreateRequest, RecordUpdateRequest, RecordVO
from app.services.family_service import assert_family_access


def _bound_ids(db: Session, user: SysUser) -> List[int]:
    return list(db.exec(select(FamilyMember.traveler_id).where(FamilyMember.user_id == user.id)).all())


def to_vo(db: Session, r: TravelRecord) -> RecordVO:
    traveler = db.get(TravelerProfile, r.traveler_id)
    return RecordVO(
        id=r.id,
        traveler_id=r.traveler_id,
        traveler_name=traveler.name if traveler else None,
        trip_id=r.trip_id,
        destination=r.destination,
        visited_date=r.visited_date,
        rating=r.rating,
        content=r.content,
        photos=r.photos,
        visibility=r.visibility,
        create_time=r.create_time,
    )


def list_records(db: Session, user: SysUser, current: int, size: int) -> tuple[List[RecordVO], int]:
    stmt = select(TravelRecord)
    count_stmt = select(func.count(TravelRecord.id))
    if user.role != "ADMIN":
        ids = _bound_ids(db, user)
        stmt = stmt.where(TravelRecord.traveler_id.in_(ids))
        count_stmt = count_stmt.where(TravelRecord.traveler_id.in_(ids))
    total = db.exec(count_stmt).one()
    records = db.exec(stmt.order_by(TravelRecord.id.desc()).offset((current - 1) * size).limit(size)).all()
    return [to_vo(db, r) for r in records], total


def create_record(db: Session, user: SysUser, payload: RecordCreateRequest) -> RecordVO:
    assert_family_access(db, user, payload.traveler_id)
    record = TravelRecord(
        traveler_id=payload.traveler_id,
        trip_id=payload.trip_id,
        destination=payload.destination,
        visited_date=payload.visited_date,
        rating=payload.rating,
        content=payload.content,
        photos=payload.photos,
        visibility=payload.visibility,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return to_vo(db, record)


def update_record(db: Session, user: SysUser, record_id: int, payload: RecordUpdateRequest) -> RecordVO:
    record = db.get(TravelRecord, record_id)
    if record is None:
        raise BusinessException("旅游记录不存在", code=404)
    assert_family_access(db, user, record.traveler_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.add(record)
    db.commit()
    db.refresh(record)
    return to_vo(db, record)


def delete_record(db: Session, user: SysUser, record_id: int) -> None:
    record = db.get(TravelRecord, record_id)
    if record is None:
        raise BusinessException("旅游记录不存在", code=404)
    assert_family_access(db, user, record.traveler_id)
    db.delete(record)
    db.commit()


def admin_list_records(db: Session, current: int, size: int, traveler_id: int | None, keyword: str, rating: int | None = None, visited_date: str = "") -> tuple[List[RecordVO], int]:
    stmt = select(TravelRecord)
    count_stmt = select(func.count(TravelRecord.id))
    if traveler_id:
        stmt = stmt.where(TravelRecord.traveler_id == traveler_id)
        count_stmt = count_stmt.where(TravelRecord.traveler_id == traveler_id)
    if keyword:
        stmt = stmt.join(TravelerProfile, TravelRecord.traveler_id == TravelerProfile.id)
        count_stmt = count_stmt.join(TravelerProfile, TravelRecord.traveler_id == TravelerProfile.id)
        cond = (TravelRecord.destination.contains(keyword)
                | TravelRecord.content.contains(keyword)
                | TravelerProfile.name.contains(keyword))
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)
    if rating is not None:
        stmt = stmt.where(TravelRecord.rating == rating)
        count_stmt = count_stmt.where(TravelRecord.rating == rating)
    if visited_date:
        try:
            d = date.fromisoformat(visited_date)
        except ValueError:
            raise BusinessException("到访日期格式应为 YYYY-MM-DD", code=400)
        stmt = stmt.where(TravelRecord.visited_date == d)
        count_stmt = count_stmt.where(TravelRecord.visited_date == d)
    total = db.exec(count_stmt).one()
    records = db.exec(stmt.order_by(TravelRecord.id.desc()).offset((current - 1) * size).limit(size)).all()
    return [to_vo(db, r) for r in records], total
