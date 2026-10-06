"""P0 必测业务不变量（对应 3.2 打卡幂等 / 3.3 防超卖 / 3.4 模板时间归一化与 use_count / 3.5 报名 upsert）。"""
import threading
from datetime import date, datetime, timedelta

from sqlmodel import Session, select

from app.common.constants import TIME_SLOTS
from app.common.exceptions import BusinessException
from app.db.session import engine
from app.models import GroupTour, SysUser, TripTemplate, TripTemplateItem, TripTodo
from app.schemas.booking import BookingOrderCreateRequest
from app.schemas.template import TemplateCopyRequest, TemplatePublishRequest
from app.schemas.trip import TodoCreateRequest, TripCreateRequest
from app.services import booking_service, template_service, todo_service, tour_service, trip_service


def _user(db):
    return db.get(SysUser, 2)  # aaa


def test_booking_oversell_concurrent():
    """3.3：同一 slot_lock 并发两单只成功一单。"""
    with Session(engine) as db:
        slots = booking_service.slots(db, "guide", 3)
        slot = slots[0].slots[0]
        catalog_id = slots[0].catalog_id
    results = []

    def worker():
        with Session(engine) as s:
            try:
                booking_service.create_order(s, _user(s), BookingOrderCreateRequest(traveler_id=1, catalog_id=catalog_id, slot=slot, guest_count=1))
                results.append("ok")
            except BusinessException:
                results.append("fail")

    ts = [threading.Thread(target=worker) for _ in range(2)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    assert results.count("ok") == 1, results
    assert results.count("fail") == 1, results


def test_todo_done_idempotent():
    """3.2：同一待办连打卡两次，不产生第二行、done_time 不变。"""
    with Session(engine) as db:
        todo_id = db.exec(select(TripTodo.id).where(TripTodo.status == 2)).first()
    with Session(engine) as db:
        u = _user(db)
        todo_service.done(db, u, todo_id)
        t1 = db.get(TripTodo, todo_id)
        todo_service.done(db, u, todo_id)  # 第二次幂等
        assert db.get(TripTodo, todo_id).done_time == t1.done_time


def test_signup_upsert():
    """3.5：同一 traveler 报名同一活动两次只留一行（第二次报已报名）。"""
    with Session(engine) as db:
        tour_id = db.exec(select(GroupTour.id).order_by(GroupTour.id)).first()
    with Session(engine) as db:
        u = _user(db)
        tour_service.signup(db, u, tour_id, 1)  # 第一次成功
        try:
            tour_service.signup(db, u, tour_id, 1)  # 第二次报已报名
            assert False, "第二次报名应报错"
        except BusinessException as e:
            assert e.code == 400


def test_template_copy_time_normalization():
    """3.4：publish 把 10:30 归一化进四值域，copy 出来与源一致。"""
    with Session(engine) as db:
        u = _user(db)
        trip = trip_service.create_trip(db, u, TripCreateRequest(traveler_id=1, title="归一化测试", start_date=date.today(), end_date=date.today() + timedelta(days=2)))
        due = datetime.combine(date.today(), datetime.strptime("10:30", "%H:%M").time())
        todo_service.create_todo(db, u, TodoCreateRequest(trip_id=trip.id, item_name="待办", due_time=due))
        tpl = template_service.publish(db, u, TemplatePublishRequest(trip_id=trip.id))
        items = db.exec(select(TripTemplateItem).where(TripTemplateItem.template_id == tpl.id)).all()
        assert items, "模板应有明细"
        for it in items:
            assert it.time_slot in TIME_SLOTS, f"time_slot 越界: {it.time_slot}"
        src_slot = items[0].time_slot
        trip2 = template_service.copy_template(db, u, tpl.id, TemplateCopyRequest(traveler_id=1, start_date=date.today() + timedelta(days=7)))
        copied = db.exec(select(TripTodo).where(TripTodo.trip_id == trip2.id)).all()
        assert copied, "复制的行程应有待办"
        expected_hm = "09:00" if src_slot == "全天" else src_slot
        for t in copied:
            assert t.due_time.strftime("%H:%M") == expected_hm, f"copy due_time 与源不一致: {t.due_time}"


def test_use_count_atomic_increment():
    """3.4：连续 copy 两次，use_count 恰好 +2。"""
    with Session(engine) as db:
        u = _user(db)
        tpl = db.exec(select(TripTemplate).order_by(TripTemplate.id)).first()
        base = tpl.use_count
        template_service.copy_template(db, u, tpl.id, TemplateCopyRequest(traveler_id=1, start_date=date.today() + timedelta(days=10)))
        template_service.copy_template(db, u, tpl.id, TemplateCopyRequest(traveler_id=1, start_date=date.today() + timedelta(days=11)))
        db.refresh(tpl)
        assert tpl.use_count == base + 2, f"use_count 应为 {base + 2}，实际 {tpl.use_count}"


def test_create_record_writes_time(client, user_headers):
    """避坑 21：create 接口真实写库（时间字段非空，不报 1048）。"""
    r = client.post("/api/records", json={"travelerId": 1, "destination": "测试目的地", "rating": 5, "content": "测试"}, headers=user_headers)
    assert r.status_code == 200
    rec = r.json()["data"]
    assert rec["id"] is not None
    assert rec["createTime"] is not None
