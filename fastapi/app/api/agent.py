"""智能助手接口（见施工规范 §6.4、§6.10 第 1622 行）。

路径：POST /api/agent/chat、GET /api/agent/sessions、GET /api/agent/sessions/{session_id}/messages。
全部登录级，只读写当前用户自己的会话。
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.agent import memory, react
from app.common.result import Result
from app.core.deps import get_current_user, get_db
from app.schemas.agent import AgentChatRequest, AgentChatResponse

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
