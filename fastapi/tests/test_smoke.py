"""P0 只读冒烟 + 攻略检索（对应 §5 三次返工 / 用户「38 端点全站只读冒烟」）。"""


def test_readonly_get_smoke(client, admin_headers):
    spec = client.get("/openapi.json").json()
    non_200 = []
    for path, methods in spec["paths"].items():
        if "get" in methods and "{" not in path:
            r = client.get(path, headers=admin_headers)
            if r.status_code != 200:
                non_200.append((path, r.status_code))
    # 关键不变量：不允许任何 500
    assert all(s != 500 for _, s in non_200), f"只读 GET 出现 500: {non_200}"
    # 其余非 200 只能是「缺必填参数」的正当 400（FastAPI 校验）
    assert all(s == 400 for _, s in non_200), f"出现非 200/400: {non_200}"


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
