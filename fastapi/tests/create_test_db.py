"""创建测试库 travel_assistant_test：改写 system.sql 的 CREATE DATABASE / USE 两行后执行。

用法：cd fastapi && .venv/Scripts/python.exe tests/create_test_db.py
前置：MySQL 在跑，.env 的 DB_USER / DB_PASSWORD 可用。
⚠️ 只动 travel_assistant_test，绝不碰 travel_assistant。
"""
import re
import sys
from pathlib import Path

# 脚本独立运行时，确保 fastapi/ 在 sys.path（import app 需要）
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pymysql

from app.core.config import settings

SQL_PATH = Path(__file__).resolve().parent.parent.parent / "sql" / "system.sql"
TEST_DB = "travel_assistant_test"


def _rewrite(text: str) -> str:
    # 1. 改写两行
    text = text.replace(
        "CREATE DATABASE IF NOT EXISTS travel_assistant ",
        "CREATE DATABASE IF NOT EXISTS travel_assistant_test ",
    )
    text = text.replace("USE travel_assistant;", "USE travel_assistant_test;")
    # 2. 断言剩余行无库级语句指向真库
    for i, line in enumerate(text.splitlines(), 1):
        low = line.strip().lower()
        if re.match(r"(create|drop|use)\s+database", low):
            if "travel_assistant_test" not in low and "travel_assistant" in low:
                raise SystemExit(f"system.sql 第 {i} 行疑似指向真库：{line.strip()}")
    return text


def _statements(text: str):
    """按分号拆分；system.sql 字符串字面量内无分号，拆分安全。"""
    for chunk in text.split(";"):
        s = chunk.strip()
        if not s:
            continue
        body = "".join(ln for ln in s.splitlines() if not ln.strip().startswith("--"))
        if body.strip():
            yield s


def main() -> None:
    text = _rewrite(SQL_PATH.read_text(encoding="utf-8"))
    conn = pymysql.connect(
        host=settings.DB_HOST, port=settings.DB_PORT,
        user=settings.DB_USER, password=settings.DB_PASSWORD, charset="utf8mb4",
    )
    try:
        with conn.cursor() as cur:
            for stmt in _statements(text):
                cur.execute(stmt)
        conn.commit()
    finally:
        conn.close()
    print(f"测试库 {TEST_DB} 已创建/重建")


if __name__ == "__main__":
    main()
