"""测试库工具：改写 system.sql 的 CREATE DATABASE / USE 两行后重建 travel_assistant_test。

被 conftest 的 session 级 autouse fixture 与 create_test_db.py 脚本共用。
"""
import re
from pathlib import Path

import pymysql

SQL_PATH = Path(__file__).resolve().parent.parent.parent / "sql" / "system.sql"


def _rewrite(text: str) -> str:
    text = text.replace(
        "CREATE DATABASE IF NOT EXISTS travel_assistant ",
        "CREATE DATABASE IF NOT EXISTS travel_assistant_test ",
    )
    text = text.replace("USE travel_assistant;", "USE travel_assistant_test;")
    for i, line in enumerate(text.splitlines(), 1):
        low = line.strip().lower()
        if re.match(r"(create|drop|use)\s+database", low):
            if "travel_assistant_test" not in low and "travel_assistant" in low:
                raise SystemExit(f"system.sql 第 {i} 行疑似指向真库：{line.strip()}")
    return text


def _statements(text: str):
    for chunk in text.split(";"):
        s = chunk.strip()
        if not s:
            continue
        body = "".join(ln for ln in s.splitlines() if not ln.strip().startswith("--"))
        if body.strip():
            yield s


def recreate_test_db(host: str, port: int, user: str, password: str) -> None:
    """DROP 后重建 travel_assistant_test（清空重建，保证测试可重复运行）。"""
    text = _rewrite(SQL_PATH.read_text(encoding="utf-8"))
    conn = pymysql.connect(host=host, port=port, user=user, password=password, charset="utf8mb4")
    try:
        with conn.cursor() as cur:
            for stmt in _statements(text):
                cur.execute(stmt)
        conn.commit()
    finally:
        conn.close()
