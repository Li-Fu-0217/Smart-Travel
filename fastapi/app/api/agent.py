"""智能助手接口（见施工规范 §6.4、§6.10 第 1622 行）。

路径：POST /api/agent/chat、GET /api/agent/sessions、GET /api/agent/sessions/{session_id}/messages。
全部登录级，只读写当前用户自己的会话。
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.agent import memory, react
from app.agent.tool_catalog import CATALOG
from app.common.result import PageResult, Result
from app.core.deps import get_current_user, get_db, require_admin
from app.schemas.agent import AgentChatRequest, AgentChatResponse
from app.services import agent_service

router = APIRouter(prefix="/agent", tags=["智能助手"])


@router.post("/chat")
def chat(payload: AgentChatRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    result = react.chat(db, current_user, payload.message, payload.session_id)
    return Result(data=AgentChatResponse(**result))


@router.get("/sessions")
def list_sessions(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=memory.list_sessions(db, current_user))


@router.get("/sessions/{session_id}/messages")
def list_messages(session_id: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=memory.list_messages(db, current_user, session_id))


# —— 管理端（绝对路径 /api/admin/agent/*，不叠 /stats 前缀，见 §4.5 避坑 24）——
admin_router = APIRouter(prefix="/admin/agent", tags=["助手管理"])


@admin_router.get("/tools")
def list_tools(current_user=Depends(require_admin), db: Session = Depends(get_db)):
    return Result(data=CATALOG)


@admin_router.get("/tool-logs")
def list_tool_logs(
    tool_name: str | None = Query(None, alias="toolName"),
    session_id: str | None = Query(None, alias="sessionId"),
    current: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    records, total = agent_service.list_tool_logs(db, tool_name, session_id, current, size)
    return Result(data=PageResult(records=records, total=total, current=current, size=size))
