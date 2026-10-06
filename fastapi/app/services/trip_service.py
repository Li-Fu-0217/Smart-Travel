"""行程服务（见施工规范 §4.1、§4.5、§4.11、§5.2）。"""
from datetime import date, datetime, time, timedelta
from typing import List, Optional

from sqlmodel import Session, delete, func, select

from app.common.exceptions import BusinessException
from app.models import BookingCatalog, BookingOrder, FamilyMember, SysUser, TripPlan, TripTodo
from app.schemas.trip import (
    TripCreateRequest,
    TripNextDayVO,
    TripTodayBookingVO,
    TripTodayOverdueItemVO,
    TripTodayTodoItemVO,
    TripTodayVO,
    TripUpdateRequest,
    TripVO,
)
from app.services.family_service import assert_family_access


def to_vo(t: TripPlan) -> TripVO:
    return TripVO(
        id=t.id,
        traveler_id=t.traveler_id,
        title=t.title,
        destination=t.destination,
        start_date=t.start_date,
        end_date=t.end_date,
        budget=t.budget,
        remark=t.remark,
        status=t.status,
        source_template_id=t.source_template_id,
        create_time=t.create_time,
        update_time=t.update_time,
    )


def _bound_ids(db: Session, user: SysUser) -> List[int]:
    return db.exec(select(FamilyMember.traveler_id).where(FamilyMember.user_id == user.id)).all()


def list_trips(db: Session, user: SysUser, current: int, size: int, keyword: str) -> tuple[List[TripVO], int]:
    stmt = select(TripPlan)
    count_stmt = select(func.count(TripPlan.id))
    if user.role != "ADMIN":
        ids = _bound_ids(db, user)
        stmt = stmt.where(TripPlan.traveler_id.in_(ids))
        count_stmt = count_stmt.where(TripPlan.traveler_id.in_(ids))
    if keyword:
        cond = TripPlan.title.contains(keyword) | TripPlan.destination.contains(keyword)
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)
    total = db.exec(count_stmt).one()
    trips = db.exec(stmt.order_by(TripPlan.id).offset((current - 1) * size).limit(size)).all()
    return [to_vo(t) for t in trips], total


def get_trip(db: Session, user: SysUser, trip_id: int) -> TripVO:
    trip = db.get(TripPlan, trip_id)
    if trip is None:
        raise BusinessException("行程不存在", code=404)
    assert_family_access(db, user, trip.traveler_id)
    return to_vo(trip)


def create_trip(db: Session, user: SysUser, payload: TripCreateRequest) -> TripVO:
    assert_family_access(db, user, payload.traveler_id)
    trip = TripPlan(
        traveler_id=payload.traveler_id,
        title=payload.title,
        destination=payload.destination,
        start_date=payload.start_date,
        end_date=payload.end_date,
        budget=payload.budget,
        remark=payload.remark,
        status=payload.status,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return to_vo(trip)


def update_trip(db: Session, user: SysUser, trip_id: int, payload: TripUpdateRequest) -> TripVO:
    trip = db.get(TripPlan, trip_id)
    if trip is None:
        raise BusinessException("行程不存在", code=404)
    assert_family_access(db, user, trip.traveler_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(trip, field, value)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return to_vo(trip)


def delete_trip(db: Session, user: SysUser, trip_id: int) -> None:
    trip = db.get(TripPlan, trip_id)
    if trip is None:
        raise BusinessException("行程不存在", code=404)
    assert_family_access(db, user, trip.traveler_id)
    db.exec(delete(TripTodo).where(TripTodo.trip_id == trip_id))
    db.delete(trip)
    db.commit()


def today(db: Session, user: SysUser, traveler_id: int) -> TripTodayVO:
    assert_family_access(db, user, traveler_id)
    today_date = date.today()

    # 逾期待办：无论有无进行中行程都要返回（§4.11 4.2 核实后推翻早退）
    overdue_todos = db.exec(
        select(TripTodo)
        .where(
            TripTodo.traveler_id == traveler_id,
            TripTodo.status == 2,
            TripTodo.due_time < datetime.now(),
        )
        .order_by(TripTodo.due_time)
    ).all()
    overdue_vos = [
        TripTodayOverdueItemVO(id=t.id, item_name=t.item_name, due_time=t.due_time, status=t.status)
        for t in overdue_todos
    ]

    active = db.exec(
        select(TripPlan)
        .where(
            TripPlan.traveler_id == traveler_id,
            TripPlan.status == 1,
            TripPlan.start_date <= today_date,
            TripPlan.end_date >= today_date,
        )
        .order_by(TripPlan.start_date)
    ).first()

    if active is None:
        return TripTodayVO(
            trip_id=None,
            title=None,
            destination=None,
            day_index=0,
            day_count=0,
            date=today_date,
            today_todos=[],
            overdue_todos=overdue_vos,
            next_days=[],
            bookings=[],
        )

    day_index = (today_date - active.start_date).days + 1
    day_count = (active.end_date - active.start_date).days + 1

    today_start = datetime.combine(today_date, time.min)
    tomorrow_start = today_start + timedelta(days=1)
    today_todos = db.exec(
        select(TripTodo)
        .where(
            TripTodo.trip_id == active.id,
            TripTodo.due_time >= today_start,
            TripTodo.due_time < tomorrow_start,
        )
        .order_by(TripTodo.due_time)
    ).all()

    next_days: List[TripNextDayVO] = []
    for offset in (1, 2):
        d = today_date + timedelta(days=offset)
        d_start = datetime.combine(d, time.min)
        d_end = d_start + timedelta(days=1)
        items = db.exec(
            select(TripTodo.item_name)
            .where(
                TripTodo.trip_id == active.id,
                TripTodo.due_time >= d_start,
                TripTodo.due_time < d_end,
            )
            .order_by(TripTodo.due_time)
        ).all()
        next_days.append(TripNextDayVO(date=d, items=list(items)))

    bookings = db.exec(
        select(BookingOrder)
        .where(
            BookingOrder.traveler_id == traveler_id,
            BookingOrder.status.in_(("pending", "confirmed")),
        )
        .order_by(BookingOrder.booking_time)
    ).all()
    booking_vos: List[TripTodayBookingVO] = []
    for b in bookings:
        catalog = db.get(BookingCatalog, b.catalog_id)
        booking_vos.append(TripTodayBookingVO(
            id=b.id,
            catalog_name=catalog.name if catalog else None,
            booking_time=b.booking_time,
            status=b.status,
        ))

    return TripTodayVO(
        trip_id=active.id,
        title=active.title,
        destination=active.destination,
        day_index=day_index,
        day_count=day_count,
        date=today_date,
        today_todos=[
            TripTodayTodoItemVO(
                id=t.id,
                item_name=t.item_name,
                time_slot=t.due_time.strftime("%H:%M") if t.due_time else None,
                status=t.status,
            )
            for t in today_todos
        ],
        overdue_todos=overdue_vos,
        next_days=next_days,
        bookings=booking_vos,
    )
