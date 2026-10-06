"""P1 回归：4.6 修的 3 个查询参数边界缺陷（先修后测，对应避坑 26 复发）。"""
from sqlmodel import Session, delete, select

from app.db.session import engine
from app.models import TripTemplate


def test_invalid_visited_date_not_500(client, admin_headers):
    for v in ["abc", "2026-13-45", "2026/07/07", "1"]:
        r = client.get("/api/admin/records", params={"visitedDate": v}, headers=admin_headers)
        assert r.status_code != 500, f"visitedDate={v!r} 不应 500"
        assert r.json()["code"] == 400, f"visitedDate={v!r} 应 body code=400"


def test_unknown_day_range_400(client, admin_headers):
    r = client.get("/api/admin/templates", params={"dayRange": "9-9"}, headers=admin_headers)
    assert r.json()["code"] == 400


def test_unknown_use_range_400(client, admin_headers):
    r = client.get("/api/admin/templates", params={"useRange": "abc"}, headers=admin_headers)
    assert r.json()["code"] == 400


def test_rating_0_not_full_list(client, admin_headers):
    r = client.get("/api/admin/records", params={"rating": 0}, headers=admin_headers)
    assert r.json()["data"]["total"] == 0  # 不能返回全量


def test_use_range_1_5_excludes_0(client, admin_headers):
    # 自己造一条 use_count=0 的模板（现有数据恰好没有 0 次，这正是 bug 藏得住的原因）
    with Session(engine) as db:
        db.add(TripTemplate(title="零使用模板", destination="测试", day_count=2, use_count=0, status=1))
        db.commit()
        zero_id = db.exec(select(TripTemplate.id).where(TripTemplate.title == "零使用模板")).first()
    try:
        r = client.get("/api/admin/templates", params={"useRange": "1-5", "size": 100}, headers=admin_headers)
        rows = r.json()["data"]["records"]
        assert all(x["useCount"] >= 1 for x in rows), "useRange=1-5 不应包含 use_count=0"
        assert all(x["id"] != zero_id for x in rows), "零使用模板不应被 1-5 命中"
    finally:
        with Session(engine) as db:
            db.exec(delete(TripTemplate).where(TripTemplate.id == zero_id))
            db.commit()
