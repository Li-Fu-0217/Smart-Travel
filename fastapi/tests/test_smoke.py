"""P0 只读冒烟 + 攻略检索（对应 §5 三次返工 / 用户「38 端点全站只读冒烟」）。"""


def test_readonly_get_smoke(client, admin_headers):
    spec = client.get("/openapi.json").json()
    non_200 = {}
    for path, methods in spec["paths"].items():
        if "get" in methods and "{" not in path:
            r = client.get(path, headers=admin_headers)
            if r.status_code != 200:
                non_200[path] = r.status_code
    # 显式列名断言那 3 个「缺必填参数」的正当 400；其余必须全 200（§13 F1）
    expected_400 = {
        "/api/files/download",   # 缺 path
        "/api/files/preview",    # 缺 path
        "/api/trips/today",      # 缺 travelerId
    }
    assert set(non_200.keys()) == expected_400, f"非 200 端点集合不符: {non_200}"
    assert all(s == 400 for s in non_200.values()), f"出现非 400: {non_200}"


def test_guide_retrieval_recall_and_score_bound(client, user_headers):
    r = client.post("/api/guides/query", json={"text": "申根签证"}, headers=user_headers)
    assert r.status_code == 200
    data = r.json()["data"]
    results = data["results"]
    assert results, "申根签证应能召回"
    # 合并分理论上限：0.6*向量(<=1) + 1.2*n-gram 命中数（§5 二次加权返工）
    # _keyword_score 统计 n in (2,3,4) 的滑动 n-gram
    n_grams = sum(max(0, len("申根签证") - n + 1) for n in (2, 3, 4))
    upper = 0.6 + 1.2 * n_grams
    for h in results:
        assert h["score"] <= upper + 1e-6, f"分数 {h['score']} 超过理论上限 {upper}"
