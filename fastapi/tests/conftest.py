"""测试夹具与红线（见施工规范 §8 避坑 37 / 用户「补后端测试」指令）。

红线：目标库名必须以 _test 结尾，否则拒绝运行——防手滑把测试跑在存有用户不可再生数据的真库上。
用法：cd fastapi && .venv/Scripts/python.exe -m pytest tests/
"""
import os

# 必须先于任何 app 导入设置：pydantic-settings 中真实环境变量优先于 .env 文件
os.environ["DB_NAME"] = "travel_assistant_test"

import pytest  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


def _assert_test_db() -> None:
    """红线：目标库名不以 _test 结尾就直接拒绝运行。"""
    if not settings.DB_NAME.endswith("_test"):
        pytest.exit(f"目标库名 {settings.DB_NAME!r} 不以 _test 结尾，拒绝运行（防测试跑在真库上）")


_assert_test_db()  # conftest 加载时立即触发，不依赖任何 fixture 被使用


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
