"""元测试：红线真的会响（§13 F1 验收）。

用真库名起一个 pytest 子进程，断言它非零退出且输出含拒绝信息。
这保证「拒绝运行」是机器每次自动检查，而不是手工改代码才看得到的证据。
"""
import os
import subprocess
import sys
from pathlib import Path

FASTAPI_DIR = Path(__file__).resolve().parent.parent


def test_red_line_rejects_real_db():
    env = dict(os.environ)
    env["DB_NAME"] = "travel_assistant"  # 真库名，不以 _test 结尾
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_auth.py::test_no_token_401", "-q"],
        env=env,
        capture_output=True,
        text=True,
        cwd=str(FASTAPI_DIR),
        timeout=120,
    )
    assert proc.returncode != 0, f"红线未触发（返回码 {proc.returncode}）"
    combined = (proc.stdout or "") + (proc.stderr or "")
    assert "不以 _test 结尾" in combined, f"输出不含拒绝信息：\n{combined}"
