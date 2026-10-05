"""拼团活动服务（见施工规范 §4.5、§5.8、避坑 27）。

报名为 upsert 语义：uk_tour_traveler(tour_id, traveler_id) 唯一，取消只改 status 不删行。
"""
from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, delete, func, select

from app.common.exceptions import BusinessException
from app.models import GroupTour, GroupTourSignup, SysUser, TravelerProfile
from app.schemas.tour import SignupVO, TourCreateRequest, TourUpdateRequest, TourVO
from app.services.family_service import assert_family_access


def to_tour_vo(t: GroupTour) -> TourVO:
    return TourVO(
        id=t.id,
        title=t.title,
        content=t.content,
        destination=t.destination,
        start_time=t.start_time,
        end_time=t.end_time,
        capacity=t.capacity,
        status=t.status,
        create_time=t.create_time,
    )


def to_signup_vo(db: Session, s: GroupTourSignup) -> SignupVO:
    tour = db.get(GroupTour, s.tour_id)
    traveler = db.get(TravelerProfile, s.traveler_id)
    account = db.get(SysUser, s.user_id)
    return SignupVO(
        id=s.id,
        tour_id=s.tour_id,
        traveler_id=s.traveler_id,
        user_id=s.user_id,
        status=s.status,
        tour_title=tour.title if tour else None,
        traveler_name=traveler.name if traveler else None,
        username=account.username if account else None,
        create_time=s.create_time,
    )


def list_tours(db: Session) -> List[TourVO]:
    tours = db.exec(select(GroupTour).where(GroupTour.status == 1).order_by(GroupTour.id)).all()
    return [to_tour_vo(t) for t in tours]


def signup(db: Session, user: SysUser, tour_id: int, traveler_id: int) -> SignupVO:
    # 先对 group_tour 行加 FOR UPDATE 锁，串行化「计数校验 + 写入」，并保证后续读视图新鲜（避坑 28）
    tour = db.exec(select(GroupTour).where(GroupTour.id == tour_id).with_for_update()).first()
    if tour is None or tour.status != 1:
        raise BusinessException("活动不存在或已结束", code=404)
    assert_family_access(db, user, traveler_id)
    # 锁定读（FOR UPDATE）读最新已提交数据，避免 REPEATABLE READ 快照读到旧计数（避坑 28）
    existing = db.exec(
        select(GroupTourSignup)
        .where(GroupTourSignup.tour_id == tour_id, GroupTourSignup.traveler_id == traveler_id)
        .with_for_update()
    ).first()
    if existing is not None and existing.status == "registered":
        raise BusinessException("你已报名该活动", code=400)
    if tour.capacity > 0:  # capacity=0 表示不限名额
        registered = db.exec(
            select(GroupTourSignup)
            .where(GroupTourSignup.tour_id == tour_id, GroupTourSignup.status == "registered")
            .with_for_update()
        ).all()
        if len(registered) >= tour.capacity:
            raise BusinessException("活动名额已满", code=400)
    try:
        if existing is not None:  # cancelled → 重新报名
            existing.status = "registered"
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return to_signup_vo(db, existing)
        signup = GroupTourSignup(tour_id=tour_id, traveler_id=traveler_id, user_id=user.id, status="registered")
        db.add(signup)
        db.commit()
        db.refresh(signup)
        return to_signup_vo(db, signup)
    except IntegrityError:
        db.rollback()
        raise BusinessException("你已报名该活动", code=400)


def my_signups(db: Session, user: SysUser) -> List[SignupVO]:
    signups = db.exec(
        select(GroupTourSignup).where(GroupTourSignup.user_id == user.id).order_by(GroupTourSignup.id.desc())
    ).all()
    return [to_signup_vo(db, s) for s in signups]


def admin_list_tours(db: Session, current: int, size: int, keyword: str) -> tuple[List[TourVO], int]:
    stmt = select(GroupTour)
    count_stmt = select(func.count(GroupTour.id))
    if keyword:
        cond = GroupTour.title.contains(keyword)
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)
    total = db.exec(count_stmt).one()
    tours = db.exec(stmt.order_by(GroupTour.id.desc()).offset((current - 1) * size).limit(size)).all()
    return [to_tour_vo(t) for t in tours], total


def admin_create_tour(db: Session, payload: TourCreateRequest) -> TourVO:
    tour = GroupTour(
        title=payload.title,
        content=payload.content,
        destination=payload.destination,
        start_time=payload.start_time,
        end_time=payload.end_time,
        capacity=payload.capacity,
        status=payload.status,
    )
    db.add(tour)
    db.commit()
    db.refresh(tour)
    return to_tour_vo(tour)


def admin_update_tour(db: Session, tour_id: int, payload: TourUpdateRequest) -> TourVO:
    tour = db.get(GroupTour, tour_id)
    if tour is None:
        raise BusinessException("活动不存在", code=404)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(tour, field, value)
    db.add(tour)
    db.commit()
    db.refresh(tour)
    return to_tour_vo(tour)


def admin_delete_tour(db: Session, tour_id: int) -> None:
    tour = db.get(GroupTour, tour_id)
    if tour is None:
        raise BusinessException("活动不存在", code=404)
    db.exec(delete(GroupTourSignup).where(GroupTourSignup.tour_id == tour_id))
    db.delete(tour)
    db.commit()


def admin_list_signups(db: Session, current: int, size: int, tour_id: Optional[int]) -> tuple[List[SignupVO], int]:
    stmt = select(GroupTourSignup)
    count_stmt = select(func.count(GroupTourSignup.id))
    if tour_id:
        stmt = stmt.where(GroupTourSignup.tour_id == tour_id)
        count_stmt = count_stmt.where(GroupTourSignup.tour_id == tour_id)
    total = db.exec(count_stmt).one()
    signups = db.exec(stmt.order_by(GroupTourSignup.id.desc()).offset((current - 1) * size).limit(size)).all()
    return [to_signup_vo(db, s) for s in signups], total
