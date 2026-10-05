"""旅行者档案服务（见施工规范 §4.1、§4.5、§5.2）。"""
from typing import List

from sqlmodel import Session, delete, func, select

from app.common.exceptions import BusinessException
from app.models import FamilyMember, SysUser, TravelerProfile
from app.schemas.traveler import (
    TravelerCreateRequest,
    TravelerProfileVO,
    TravelerUpdateRequest,
    TravelerVO,
)
from app.services.family_service import assert_family_access


def to_vo(t: TravelerProfile) -> TravelerVO:
    return TravelerVO(
        id=t.id,
        name=t.name,
        gender=t.gender,
        birth_date=t.birth_date,
        phone=t.phone,
        status=t.status,
        preferences=t.preferences,
        preference_tags=t.preference_tags,
        create_time=t.create_time,
        update_time=t.update_time,
    )


def to_profile_vo(t: TravelerProfile) -> TravelerProfileVO:
    return TravelerProfileVO(
        id=t.id,
        name=t.name,
        gender=t.gender,
        birth_date=t.birth_date,
        phone=t.phone,
        id_card_no=t.id_card_no,
        dietary_restrictions=t.dietary_restrictions,
        allergies=t.allergies,
        mobility_notes=t.mobility_notes,
        preferences=t.preferences,
        preference_tags=t.preference_tags,
        preference_summary=t.preference_summary,
        preference_updated_at=t.preference_updated_at,
        emergency_contact=t.emergency_contact,
        emergency_phone=t.emergency_phone,
        status=t.status,
        create_time=t.create_time,
        update_time=t.update_time,
    )


def _bound_ids(db: Session, user: SysUser) -> List[int]:
    return db.exec(select(FamilyMember.traveler_id).where(FamilyMember.user_id == user.id)).all()


def list_travelers(db: Session, user: SysUser, current: int, size: int, keyword: str) -> tuple[List[TravelerVO], int]:
    stmt = select(TravelerProfile)
    count_stmt = select(func.count(TravelerProfile.id))
    if user.role != "ADMIN":
        ids = _bound_ids(db, user)
        stmt = stmt.where(TravelerProfile.id.in_(ids))
        count_stmt = count_stmt.where(TravelerProfile.id.in_(ids))
    if keyword:
        cond = TravelerProfile.name.contains(keyword)
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)
    total = db.exec(count_stmt).one()
    travelers = db.exec(stmt.order_by(TravelerProfile.id).offset((current - 1) * size).limit(size)).all()
    return [to_vo(t) for t in travelers], total


def list_my_travelers(db: Session, user: SysUser) -> List[TravelerVO]:
    if user.role == "ADMIN":
        return []
    ids = _bound_ids(db, user)
    travelers = db.exec(
        select(TravelerProfile).where(TravelerProfile.id.in_(ids)).order_by(TravelerProfile.id)
    ).all()
    return [to_vo(t) for t in travelers]


def get_traveler(db: Session, user: SysUser, traveler_id: int) -> TravelerVO:
    assert_family_access(db, user, traveler_id)
    traveler = db.get(TravelerProfile, traveler_id)
    if traveler is None:
        raise BusinessException("旅行者不存在", code=404)
    return to_vo(traveler)


def get_profile(db: Session, user: SysUser, traveler_id: int) -> TravelerProfileVO:
    assert_family_access(db, user, traveler_id)
    traveler = db.get(TravelerProfile, traveler_id)
    if traveler is None:
        raise BusinessException("旅行者不存在", code=404)
    return to_profile_vo(traveler)


def create_traveler(db: Session, user: SysUser, payload: TravelerCreateRequest) -> TravelerVO:
    traveler = TravelerProfile(
        name=payload.name,
        gender=payload.gender,
        birth_date=payload.birth_date,
        phone=payload.phone,
        id_card_no=payload.id_card_no,
        dietary_restrictions=payload.dietary_restrictions,
        allergies=payload.allergies,
        mobility_notes=payload.mobility_notes,
        preferences=payload.preferences,
        emergency_contact=payload.emergency_contact,
        emergency_phone=payload.emergency_phone,
        status=payload.status,
    )
    db.add(traveler)
    db.flush()
    if user.role != "ADMIN":
        db.add(FamilyMember(user_id=user.id, traveler_id=traveler.id, is_primary=1))
    db.commit()
    db.refresh(traveler)
    return to_vo(traveler)


def update_traveler(db: Session, user: SysUser, traveler_id: int, payload: TravelerUpdateRequest) -> TravelerVO:
    assert_family_access(db, user, traveler_id)
    traveler = db.get(TravelerProfile, traveler_id)
    if traveler is None:
        raise BusinessException("旅行者不存在", code=404)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(traveler, field, value)
    db.add(traveler)
    db.commit()
    db.refresh(traveler)
    return to_vo(traveler)


def delete_traveler(db: Session, user: SysUser, traveler_id: int) -> None:
    assert_family_access(db, user, traveler_id)
    traveler = db.get(TravelerProfile, traveler_id)
    if traveler is None:
        raise BusinessException("旅行者不存在", code=404)
    db.exec(delete(FamilyMember).where(FamilyMember.traveler_id == traveler_id))
    db.delete(traveler)
    db.commit()
