"""F4 · 入参边界校验（§13 六条硬条款）。每条对应一个「非法样本 → 期望行为」。"""


# ===== 硬条款 2：枚举取值一律白名单，不在白名单 → 400 =====

def test_booking_status_whitelist_admin(client, admin_headers):
    r = client.get("/api/admin/booking/orders", params={"status": "foo"}, headers=admin_headers)
    assert r.json()["code"] == 400


def test_booking_status_whitelist_user(client, user_headers):
    r = client.get("/api/booking/orders", params={"status": "foo"}, headers=user_headers)
    assert r.json()["code"] == 400


def test_alert_status_whitelist_admin(client, admin_headers):
    r = client.get("/api/admin/alerts", params={"status": "foo"}, headers=admin_headers)
    assert r.json()["code"] == 400


def test_alert_status_whitelist_user(client, user_headers):
    r = client.get("/api/alerts", params={"status": "foo"}, headers=user_headers)
    assert r.json()["code"] == 400


def test_item_type_whitelist(client, user_headers):
    r = client.get("/api/booking/slots", params={"itemType": "foo"}, headers=user_headers)
    assert r.json()["code"] == 400


def test_logs_type_whitelist(client, admin_headers):
    r = client.get("/api/logs", params={"type": "foo"}, headers=admin_headers)
    assert r.json()["code"] == 400


def test_day_range_whitelist(client, admin_headers):
    r = client.get("/api/admin/templates", params={"dayRange": "9-9"}, headers=admin_headers)
    assert r.json()["code"] == 400


def test_use_range_whitelist(client, admin_headers):
    r = client.get("/api/admin/templates", params={"useRange": "abc"}, headers=admin_headers)
    assert r.json()["code"] == 400


# ===== 硬条款 3：日期 / 数字必须显式 try-parse，不许 500 =====

def test_visited_date_invalid_format(client, admin_headers):
    r = client.get("/api/admin/records", params={"visitedDate": "abc"}, headers=admin_headers)
    assert r.status_code != 500
    assert r.json()["code"] == 400


def test_visited_date_invalid_month(client, admin_headers):
    r = client.get("/api/admin/records", params={"visitedDate": "2026-13-45"}, headers=admin_headers)
    assert r.status_code != 500
    assert r.json()["code"] == 400


def test_rating_non_int(client, admin_headers):
    r = client.get("/api/admin/records", params={"rating": "abc"}, headers=admin_headers)
    assert r.status_code == 400  # FastAPI int 解析失败 → 422 → 400


def test_days_non_int(client, user_headers):
    r = client.get("/api/booking/slots", params={"days": "abc"}, headers=user_headers)
    assert r.status_code == 400


def test_traveler_id_non_int(client, user_headers):
    r = client.get("/api/trips/today", params={"travelerId": "abc"}, headers=user_headers)
    assert r.status_code == 400


def test_booking_slot_invalid_format(client, user_headers):
    r = client.post("/api/booking/orders", json={"travelerId": 1, "catalogId": 1, "slot": "bad-slot", "guestCount": 1}, headers=user_headers)
    assert r.json()["code"] == 400


# ===== 硬条款 5：分页参数要有上界 =====

def test_size_upper_bound(client, admin_headers):
    r = client.get("/api/admin/templates", params={"size": 101}, headers=admin_headers)
    assert r.status_code == 400


def test_size_lower_bound(client, admin_headers):
    r = client.get("/api/admin/templates", params={"size": 0}, headers=admin_headers)
    assert r.status_code == 400


def test_current_lower_bound(client, admin_headers):
    r = client.get("/api/admin/templates", params={"current": 0}, headers=admin_headers)
    assert r.status_code == 400


def test_days_upper_bound(client, user_headers):
    r = client.get("/api/booking/slots", params={"days": 999}, headers=user_headers)
    assert r.status_code == 400  # le=30


# ===== 硬条款 6：错误码位置一致（业务 200 + body code；401/403/404 → HTTP）=====

def test_business_error_http_200_body_code(client, user_headers):
    r = client.get("/api/booking/slots", params={"itemType": "foo"}, headers=user_headers)
    assert r.status_code == 200
    assert r.json()["code"] == 400


def test_not_found_http_404(client, admin_headers):
    r = client.get("/api/travelers/999999/profile", headers=admin_headers)
    assert r.status_code == 404


# ===== 硬条款 1：外部输入在接口层校验（body 枚举/长度）=====

def test_alert_body_invalid_type(client, user_headers):
    r = client.post("/api/alerts/sos", json={"travelerId": 1, "alertType": "foo", "source": "agent"}, headers=user_headers)
    assert r.status_code == 400  # AlertCreateRequest 校验器 → 422 → 400


def test_traveler_body_empty_name(client, user_headers):
    r = client.post("/api/travelers", json={"name": ""}, headers=user_headers)
    assert r.status_code == 400  # min_length=1 → 422 → 400


def test_record_body_invalid_rating(client, user_headers):
    r = client.post("/api/records", json={"travelerId": 1, "destination": "x", "rating": 9}, headers=user_headers)
    assert r.status_code == 400  # rating ge=1 le=5 → 422 → 400


# ===== F4 缺口修复：role / status / doc_type 白名单 =====

def test_user_role_whitelist_create(client, admin_headers):
    r = client.post("/api/users", json={"username": "zz", "password": "p", "role": "zzz"}, headers=admin_headers)
    assert r.status_code == 400

def test_user_role_whitelist_update(client, admin_headers):
    r = client.put("/api/users/1", json={"role": "x"}, headers=admin_headers)
    assert r.status_code == 400

def test_traveler_status_whitelist(client, user_headers):
    r = client.post("/api/travelers", json={"name": "n", "status": 7}, headers=user_headers)
    assert r.status_code == 400

def test_template_status_whitelist(client, admin_headers):
    r = client.put("/api/admin/templates/1", json={"status": 7}, headers=admin_headers)
    assert r.status_code == 400

def test_tour_status_whitelist(client, admin_headers):
    r = client.post("/api/admin/tours", json={"title": "t", "status": 7}, headers=admin_headers)
    assert r.status_code == 400

def test_guide_doc_type_whitelist():
    from pydantic import ValidationError
    from app.api.guides import GuideDocumentCreateRequest
    try:
        GuideDocumentCreateRequest(title="x", file_path="seed/x.txt", doc_type="foo")
        assert False, "doc_type=foo 应被拒"
    except ValidationError:
        pass


def test_record_visibility_whitelist(client, user_headers):
    r = client.post("/api/records", json={"travelerId": 1, "destination": "x", "visibility": 99}, headers=user_headers)
    assert r.status_code == 400
