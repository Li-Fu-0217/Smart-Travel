"""家庭绑定服务（见施工规范 §4.3、§4.5、§5.2）。

数据隔离核心闸门 assert_family_access 定义于此，被所有业务域 service 复用。
"""
from typing import List

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, func, select

from app.common.exceptions import BusinessException
from app.models import FamilyMember, SysUser, TravelerProfile
from app.schemas.family import FamilyBindingVO


def assert_family_access(db: Session, user: SysUser, traveler_id: int) -> None:
    """管理员放行；普通用户必须已绑定该旅行者，否则 403。"""
    if user.role == "ADMIN":
        return
    bound = db.exec(
        select(FamilyMember).where(
            FamilyMember.user_id == user.id,
            FamilyMember.traveler_id == traveler_id,
        )
    ).first()
    if bound is None:
        raise BusinessException("无权访问该旅行者数据", code=403)


def _to_vo(member: FamilyMember, traveler: TravelerProfile | None, username: str | None) -> FamilyBindingVO:
    return FamilyBindingVO(
        id=member.id,
        user_id=member.user_id,
        traveler_id=member.traveler_id,
        relation=member.relation,
        is_primary=member.is_primary,
        username=username,
        traveler_name=traveler.name if traveler else None,
        create_time=member.create_time,
    )


def bind(db: Session, user: SysUser, name: str, phone: str, relation: str | None, is_primary: int) -> FamilyBindingVO:
    traveler = db.exec(
        select(TravelerProfile).where(TravelerProfile.name == name, TravelerProfile.phone == phone)
    ).first()
    if traveler is None:
        raise BusinessException("未找到该旅行者档案", code=404)
    member = FamilyMember(user_id=user.id, traveler_id=traveler.id, relation=relation, is_primary=is_primary)
    db.add(member)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise BusinessException("该旅行者已被绑定", code=400)
    db.refresh(member)
    return _to_vo(member, traveler, user.username)


def unbind(db: Session, user: SysUser, binding_id: int) -> None:
    member = db.get(FamilyMember, binding_id)
    if member is None:
        raise BusinessException("绑定关系不存在", code=404)
    if user.role != "ADMIN" and member.user_id != user.id:
        raise BusinessException("无权操作该绑定", code=403)
    db.delete(member)
    db.commit()


def list_bindings(db: Session, user: SysUser) -> List[FamilyBindingVO]:
    members = db.exec(
        select(FamilyMember).where(FamilyMember.user_id == user.id).order_by(FamilyMember.id)
    ).all()
    return [_to_vo(m, db.get(TravelerProfile, m.traveler_id), user.username) for m in members]


def admin_list_family(db: Session, current: int, size: int, keyword: str) -> tuple[List[FamilyBindingVO], int]:
    stmt = select(FamilyMember)
    count_stmt = select(func.count(FamilyMember.id))
    if keyword:
        ids = db.exec(
            select(FamilyMember.id)
            .join(TravelerProfile, FamilyMember.traveler_id == TravelerProfile.id)
            .where(TravelerProfile.name.contains(keyword))
        ).all()
        stmt = stmt.where(FamilyMember.id.in_(ids))
        count_stmt = count_stmt.where(FamilyMember.id.in_(ids))
    total = db.exec(count_stmt).one()
    members = db.exec(stmt.order_by(FamilyMember.id).offset((current - 1) * size).limit(size)).all()
    vos = []
    for m in members:
        traveler = db.get(TravelerProfile, m.traveler_id)
        account = db.get(SysUser, m.user_id)
        vos.append(_to_vo(m, traveler, account.username if account else None))
    return vos, total


def admin_bind(db: Session, user_id: int, traveler_id: int, relation: str | None, is_primary: int) -> FamilyBindingVO:
    account = db.get(SysUser, user_id)
    if account is None:
        raise BusinessException("用户不存在", code=404)
    traveler = db.get(TravelerProfile, traveler_id)
    if traveler is None:
        raise BusinessException("旅行者不存在", code=404)
    member = FamilyMember(user_id=user_id, traveler_id=traveler_id, relation=relation, is_primary=is_primary)
    db.add(member)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise BusinessException("该旅行者已被绑定", code=400)
    db.refresh(member)
    return _to_vo(member, traveler, account.username)


def admin_unbind(db: Session, binding_id: int) -> None:
    member = db.get(FamilyMember, binding_id)
    if member is None:
        raise BusinessException("绑定关系不存在", code=404)
    db.delete(member)
    db.commit()
