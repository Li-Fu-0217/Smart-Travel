"""Docker 建库脚本：等 MySQL 就绪 → 改写 system.sql 库名 → 执行建表 + 种子。

⚠️ 红线：system.sql 写死 USE travel_assistant + 22 张表 DROP TABLE。
本脚本把它改写到 settings.DB_NAME（compose 里显式设为 travel_assistant_docker），
绝不指向宿主机正在用的 travel_assistant。
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "/app")  # 让 import app 可用

import pymysql  # noqa: E402

from app.core.config import settings  # noqa: E402


def _wait_db() -> None:
    for _ in range(60):
        try:
            conn = pymysql.connect(
                host=settings.DB_HOST, port=settings.DB_PORT,
                user=settings.DB_USER, password=settings.DB_PASSWORD, charset="utf8mb4",
            )
            conn.close()
            return
        except Exception:
            time.sleep(2)
    raise RuntimeError("MySQL 未就绪")


def _init() -> None:
    sql = Path("/sql/system.sql").read_text(encoding="utf-8")
    db = settings.DB_NAME  # travel_assistant_docker
    # 守卫 1：绝不把建库目标指向宿主机 travel_assistant（用户不可再生数据）
    if db == "travel_assistant":
        raise RuntimeError("拒绝把建库目标指向宿主机 travel_assistant")
    sql = sql.replace(
        "CREATE DATABASE IF NOT EXISTS travel_assistant ",
        f"CREATE DATABASE IF NOT EXISTS {db} ",
    )
    sql = sql.replace("USE travel_assistant;", f"USE {db};")
    # 守卫 2：两处 replace 必须真的生效，否则说明 system.sql 结构变了、没改写干净
    if "USE travel_assistant;" in sql or f"USE {db};" not in sql:
        raise RuntimeError("system.sql 库名改写不完整，拒绝建库")
    conn = pymysql.connect(
        host=settings.DB_HOST, port=settings.DB_PORT,
        user=settings.DB_USER, password=settings.DB_PASSWORD, charset="utf8mb4",
    )
    try:
        with conn.cursor() as cur:
            for chunk in sql.split(";"):
                s = chunk.strip()
                if not s:
                    continue
                if all(line.strip().startswith("--") for line in s.splitlines()):
                    continue
                cur.execute(s)
        conn.commit()
    finally:
        conn.close()
    print(f"建库完成：{db}")


if __name__ == "__main__":
    _wait_db()
    _init()
