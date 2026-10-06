"""行程模板服务（见施工规范 §4.5、§5.2、§5.8）。"""
from datetime import datetime, timedelta
from typing import List

from sqlmodel import Session, delete, func, select, update

from app.common.exceptions import BusinessException
from app.models import SysUser, TripPlan, TripTemplate, TripTemplateItem, TripTodo
from app.schemas.template import (
    TemplateCopyRequest,
    TemplateDetailVO,
    TemplateItemVO,
    TemplatePublishRequest,
    TemplateUpdateRequest,
    TemplateVO,
)
from app.common.constants import TIME_SLOTS
from app.services.family_service import assert_family_access
from app.services.trip_service import to_vo as trip_to_vo

# 三个具体时刻（从 TIME_SLOTS 推导，不含"全天"）；发布/复制共用，不手抄副本（§5.8）
_CONCRETE_TIMES = tuple(sorted(t for t in TIME_SLOTS if t != "全天"))


def _hm_to_minutes(hm: str) -> int:
    return int(hm[:2]) * 60 + int(hm[3:5])


def _due_time_to_time_slot(hm: str | None) -> str | None:
    """待办 HH:MM → 模板 time_slot（publish）：精确命中取原值，否则就近归档；空 → None。"""
    if hm is None:
        return None
    if hm in _CONCRETE_TIMES:
        return hm
    minutes = _hm_to_minutes(hm)
    best = _CONCRETE_TIMES[0]
    best_diff = abs(minutes - _hm_to_minutes(best))
    for t in _CONCRETE_TIMES[1:]:
        diff = abs(minutes - _hm_to_minutes(t))
        if diff < best_diff:
            best, best_diff = t, diff
    return best


def _time_slot_to_hm(time_slot: str | None) -> str | None:
    """模板 time_slot → 待办 HH:MM（copy）：三档取原值，全天 → 09:00，越界报错不兜底。"""
    if time_slot is None:
        return None
    if time_slot in _CONCRETE_TIMES:
        return time_slot
    if time_slot == "全天":
        # 库里没有"日期级"时间表达，且 §4.11 today 视图按 HH:MM 展示时段，故全天归档到 09:00
        return "09:00"
    raise BusinessException("模板时段不合法", code=400)


def _to_item_vo(item: TripTemplateItem) -> TemplateItemVO:
    return TemplateItemVO(
        id=item.id,
        template_id=item.template_id,
        day_index=item.day_index,
        time_slot=item.time_slot,
        item_name=item.item_name,
        category=item.category,
        remark=item.remark,
        sort_order=item.sort_order,
    )


def to_vo(t: TripTemplate) -> TemplateVO:
    return TemplateVO(
        id=t.id,
        title=t.title,
        destination=t.destination,
        day_count=t.day_count,
        description=t.description,
        author_user_id=t.author_user_id,
        author_name=t.author_name,
        cover=t.cover,
        use_count=t.use_count,
        status=t.status,
        create_time=t.create_time,
    )


def to_detail_vo(db: Session, t: TripTemplate) -> TemplateDetailVO:
    items = db.exec(
        select(TripTemplateItem)
        .where(TripTemplateItem.template_id == t.id)
        .order_by(TripTemplateItem.day_index, TripTemplateItem.sort_order)
    ).all()
    return TemplateDetailVO(**to_vo(t).model_dump(), items=[_to_item_vo(i) for i in items])


def list_templates(db: Session) -> List[TemplateVO]:
    templates = db.exec(
        select(TripTemplate).where(TripTemplate.status == 1).order_by(TripTemplate.id.desc())
    ).all()
    return [to_vo(t) for t in templates]


def get_template(db: Session, template_id: int) -> TemplateDetailVO:
    template = db.get(TripTemplate, template_id)
    if template is None:
        raise BusinessException("模板不存在", code=404)
    return to_detail_vo(db, template)


def publish(db: Session, user: SysUser, payload: TemplatePublishRequest) -> TemplateVO:
    trip = db.get(TripPlan, payload.trip_id)
    if trip is None:
        raise BusinessException("行程不存在", code=404)
    assert_family_access(db, user, trip.traveler_id)
    day_count = 1
    if trip.start_date and trip.end_date:
        day_count = (trip.end_date - trip.start_date).days + 1
    template = TripTemplate(
        title=payload.title or trip.title or "未命名行程",
        destination=trip.destination,
        day_count=day_count,
        description=payload.description,
        author_user_id=user.id,
        author_name=user.username,
        status=1,
    )
    db.add(template)
    db.flush()
    todos = db.exec(
        select(TripTodo).where(TripTodo.trip_id == trip.id).order_by(TripTodo.due_time, TripTodo.id)
    ).all()
    for i, todo in enumerate(todos):
        day_index = 1
        time_slot = None
        if todo.due_time:
            if trip.start_date:
                day_index = (todo.due_time.date() - trip.start_date).days + 1
            time_slot = _due_time_to_time_slot(todo.due_time.strftime("%H:%M"))
        db.add(TripTemplateItem(
            template_id=template.id,
            day_index=day_index,
            time_slot=time_slot,
            item_name=todo.item_name,
            category=todo.category,
            sort_order=i + 1,
        ))
    db.commit()
    db.refresh(template)
    return to_vo(template)


def copy_template(db: Session, user: SysUser, template_id: int, payload: TemplateCopyRequest):
    assert_family_access(db, user, payload.traveler_id)
    template = db.get(TripTemplate, template_id)
    if template is None or template.status != 1:
        raise BusinessException("模板不存在或已下架", code=404)
    items = db.exec(
        select(TripTemplateItem)
        .where(TripTemplateItem.template_id == template_id)
        .order_by(TripTemplateItem.day_index, TripTemplateItem.sort_order)
    ).all()

    start_date = payload.start_date
    end_date = start_date + timedelta(days=template.day_count - 1)
    trip = TripPlan(
        traveler_id=payload.traveler_id,
        title=template.title,
        destination=template.destination,
        start_date=start_date,
        end_date=end_date,
        status=1,
        source_template_id=template.id,
    )
    db.add(trip)
    db.flush()

    for item in items:
        due_date = start_date + timedelta(days=item.day_index - 1)
        hm = _time_slot_to_hm(item.time_slot)
        due_time = datetime.combine(due_date, datetime.strptime(hm, "%H:%M").time()) if hm else None
        db.add(TripTodo(
            trip_id=trip.id,
            traveler_id=payload.traveler_id,
            item_name=item.item_name,
            due_time=due_time,
            category=item.category,
            status=2,
        ))

    # use_count 原子自增（避免并发复制丢计数）
    db.exec(
        update(TripTemplate)
        .where(TripTemplate.id == template_id)
        .values(use_count=TripTemplate.use_count + 1)
    )
    db.commit()
    db.refresh(trip)
    return trip_to_vo(trip)


def admin_list_templates(db: Session, current: int, size: int, keyword: str, day_range: str = "", use_range: str = "") -> tuple[List[TemplateVO], int]:
    stmt = select(TripTemplate)
    count_stmt = select(func.count(TripTemplate.id))
    if keyword:
        cond = (TripTemplate.title.contains(keyword)
                | TripTemplate.destination.contains(keyword)
                | TripTemplate.author_name.contains(keyword))
        # 状态中文标签 → 值映射（§4.6）：该页无状态下拉，故并入 keyword
        if "上架" in keyword:
            cond = cond | (TripTemplate.status == 1)
        if "下架" in keyword:
            cond = cond | (TripTemplate.status == 0)
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)
    if day_range == "1-2":
        stmt = stmt.where(TripTemplate.day_count <= 2)
        count_stmt = count_stmt.where(TripTemplate.day_count <= 2)
    elif day_range == "3-4":
        stmt = stmt.where(TripTemplate.day_count >= 3, TripTemplate.day_count <= 4)
        count_stmt = count_stmt.where(TripTemplate.day_count >= 3, TripTemplate.day_count <= 4)
    elif day_range == "5+":
        stmt = stmt.where(TripTemplate.day_count >= 5)
        count_stmt = count_stmt.where(TripTemplate.day_count >= 5)
    if use_range == "1-5":
        stmt = stmt.where(TripTemplate.use_count <= 5)
        count_stmt = count_stmt.where(TripTemplate.use_count <= 5)
    elif use_range == "6+":
        stmt = stmt.where(TripTemplate.use_count >= 6)
        count_stmt = count_stmt.where(TripTemplate.use_count >= 6)
    total = db.exec(count_stmt).one()
    templates = db.exec(stmt.order_by(TripTemplate.id.desc()).offset((current - 1) * size).limit(size)).all()
    return [to_vo(t) for t in templates], total


def admin_update_template(db: Session, template_id: int, payload: TemplateUpdateRequest) -> TemplateVO:
    template = db.get(TripTemplate, template_id)
    if template is None:
        raise BusinessException("模板不存在", code=404)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    db.add(template)
    db.commit()
    db.refresh(template)
    return to_vo(template)


def admin_delete_template(db: Session, template_id: int) -> None:
    template = db.get(TripTemplate, template_id)
    if template is None:
        raise BusinessException("模板不存在", code=404)
    db.exec(delete(TripTemplateItem).where(TripTemplateItem.template_id == template_id))
    db.delete(template)
    db.commit()
