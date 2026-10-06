"""智能助手出入参（见施工规范 §6.4、§6.10、§6.12）。"""
from pydantic import Field

from app.common.result import CamelModel


class AgentChatRequest(CamelModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = Field(None, max_length=64)


class AgentChatResponse(CamelModel):
    """接口返回体（§6.4）：sessionId/reply/steps/pendingConfirm/demoMode/engine，外加 card。"""

    session_id: str
    reply: str
    steps: list[dict] = []
    pending_confirm: dict | None = None
    demo_mode: bool = True
    engine: str = "demo"
    card: dict | None = None
