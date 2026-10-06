"""元测试：红线真的会响（§13 F1 验收）。

用真库名起一个 pytest 子进程，断言它非零退出且输出含拒绝信息。
注意：子进程的编解码必须显式钉死（encoding="utf-8" + 子进程 PYTHONIOENCODING=utf-8），
否则本机 locale 是 cp936、shell 里 PYTHONIOENCODING=utf-8 时会 UnicodeDecodeError，
父进程拿到空 stdout，断言失败——这条测试就会变成「取决于环境」的不确定测试。
"""
import os
import subprocess
import sys
from pathlib import Path

FASTAPI_DIR = Path(__file__).resolve().parent.parent


def test_red_line_rejects_real_db():
    env = dict(os.environ)
    env["DB_NAME"] = "travel_assistant"  # 真库名，不以 _test 结尾
    env["PYTHONIOENCODING"] = "utf-8"  # 父子两端编码一致，与机器 locale 无关
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_auth.py::test_no_token_401", "-q"],
        env=env,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(FASTAPI_DIR),
        timeout=120,
    )
    # 非零退出（pytest.exit 于 conftest 加载时触发 → ExitCode.USAGE_ERROR = 4）
    assert proc.returncode == 4, f"红线退出码应为 4，实际 {proc.returncode}"
    combined = (proc.stdout or "") + (proc.stderr or "")
    # ASCII 标记（编码无关，任何 locale 都能匹配）+ 中文拒绝信息（钉死语义）
    assert "Exit" in combined, f"输出不含 pytest Exit 标识：\n{combined}"
    assert "不以 _test 结尾" in combined, f"输出不含拒绝信息：\n{combined}"
