"""测试夹具与红线（见 §13 F1）。

红线：目标库名必须以 _test 结尾，否则拒绝运行——防手滑把测试跑在存有用户不可再生数据的真库上。
用法：cd fastapi && .venv/Scripts/python.exe -m pytest tests/
"""
import os

# 用 setdefault：外部环境若显式把 DB_NAME 指向真库，这里不覆盖，红线就会响。
os.environ.setdefault("DB_NAME", "travel_assistant_test")

import pytest  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.main import app  # noqa: E402
from db_utils import recreate_test_db  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


def _assert_test_db() -> None:
    if not settings.DB_NAME.endswith("_test"):
        pytest.exit(f"目标库名 {settings.DB_NAME!r} 不以 _test 结尾，拒绝运行（防测试跑在真库上）")


_assert_test_db()  # conftest 加载时立即触发，不依赖任何 fixture 被使用


@pytest.fixture(scope="session", autouse=True)
def _fresh_test_db():
    """每轮 pytest 会话开始前重建测试库，保证「连续跑两次都通过、重复跑 N 次不残留」。"""
    recreate_test_db(settings.DB_HOST, settings.DB_PORT, settings.DB_USER, settings.DB_PASSWORD)


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def admin_headers():
    from app.core.security import create_access_token

    return {"Authorization": f"Bearer {create_access_token('admin')}"}


@pytest.fixture()
def user_headers():
    from app.core.security import create_access_token

    return {"Authorization": f"Bearer {create_access_token('aaa')}"}
