"""鉴权矩阵（P0，对应「USER 访问 /admin/** 被拦截」等历史事故）。"""


def test_no_token_401(client):
    r = client.get("/api/users")
    assert r.status_code == 401


def test_user_admin_403(client, user_headers):
    r = client.get("/api/users", headers=user_headers)
    assert r.status_code == 403


def test_user_foreign_traveler_profile_403(client, user_headers):
    # aaa 绑定 traveler 1；traveler 2 属于 bbb → 归属校验 403
    r = client.get("/api/travelers/2/profile", headers=user_headers)
    assert r.status_code == 403


def test_admin_can_access_admin(client, admin_headers):
    r = client.get("/api/users", headers=admin_headers)
    assert r.status_code == 200
