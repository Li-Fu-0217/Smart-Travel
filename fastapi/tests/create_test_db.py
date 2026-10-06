"""创建测试库 travel_assistant_test（独立脚本，供首次手动建库 / 单独验证）。

用法：cd fastapi && .venv/Scripts/python.exe tests/create_test_db.py
说明：pytest 的 session 级 autouse fixture 每轮会自动重建测试库，本脚本仅用于手动建库。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # fastapi/ 供 import app

from db_utils import recreate_test_db  # tests/ 是脚本目录，天然在 sys.path[0]
from app.core.config import settings


def main() -> None:
    recreate_test_db(settings.DB_HOST, settings.DB_PORT, settings.DB_USER, settings.DB_PASSWORD)
    print("测试库 travel_assistant_test 已创建/重建")


if __name__ == "__main__":
    main()
