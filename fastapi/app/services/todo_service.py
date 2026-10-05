"""行程待办服务（见施工规范 §4.5、§4.11、§5.2）。"""
from datetime import datetime
from typing import List

from sqlmodel import Session, select

from app.common.exceptions import BusinessException
from app.models import SysUser, TripPlan, TripTodo
from app.schemas.trip import TodoCreateRequest, TodoUpdateRequest, TodoVO
from app.services.family_service import assert_family_access


def to_vo(t: TripTodo) -> TodoVO:
    return TodoVO(
        id=t.id,
        trip_id=t.trip_id,
        traveler_id=t.traveler_id,
        item_name=t.item_name,
        due_time=t.due_time,
        category=t.category,
        status=t.status,
        done_time=t.done_time,
        create_time=t.create_time,
    )


def _get_trip(db: Session, trip_id: int) -> TripPlan:
    trip = db.get(TripPlan, trip_id)
    if trip is None:
        raise BusinessException("行程不存在", code=404)
    return trip


def list_todos(db: Session, user: SysUser, trip_id: int) -> List[TodoVO]:
    trip = _get_trip(db, trip_id)
    assert_family_access(db, user, trip.traveler_id)
    todos = db.exec(
        select(TripTodo).where(TripTodo.trip_id == trip_id).order_by(TripTodo.due_time, TripTodo.id)
    ).all()
    return [to_vo(t) for t in todos]


def create_todo(db: Session, user: SysUser, payload: TodoCreateRequest) -> TodoVO:
    trip = _get_trip(db, payload.trip_id)
    assert_family_access(db, user, trip.traveler_id)
    todo = TripTodo(
        trip_id=trip.id,
        traveler_id=trip.traveler_id,
        item_name=payload.item_name,
        due_time=payload.due_time,
        category=payload.category,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return to_vo(todo)


def update_todo(db: Session, user: SysUser, todo_id: int, payload: TodoUpdateRequest) -> TodoVO:
    todo = db.get(TripTodo, todo_id)
    if todo is None:
        raise BusinessException("待办不存在", code=404)
    assert_family_access(db, user, todo.traveler_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return to_vo(todo)


def delete_todo(db: Session, user: SysUser, todo_id: int) -> None:
    todo = db.get(TripTodo, todo_id)
    if todo is None:
        raise BusinessException("待办不存在", code=404)
    assert_family_access(db, user, todo.traveler_id)
    db.delete(todo)
    db.commit()


def done(db: Session, user: SysUser, todo_id: int) -> TodoVO:
    """幂等打卡：首次置 status=1 + done_time=now；再次调用不报错、done_time 不被覆盖。"""
    todo = db.get(TripTodo, todo_id)
    if todo is None:
        raise BusinessException("待办不存在", code=404)
    assert_family_access(db, user, todo.traveler_id)
    if todo.status != 1:
        todo.status = 1
        todo.done_time = datetime.now()
        db.add(todo)
        db.commit()
        db.refresh(todo)
    return to_vo(todo)


def undo(db: Session, user: SysUser, todo_id: int) -> TodoVO:
    todo = db.get(TripTodo, todo_id)
    if todo is None:
        raise BusinessException("待办不存在", code=404)
    assert_family_access(db, user, todo.traveler_id)
    todo.status = 2
    todo.done_time = None
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return to_vo(todo)
