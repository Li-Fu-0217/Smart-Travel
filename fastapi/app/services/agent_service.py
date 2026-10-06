"""智能助手管理端服务（见施工规范 §6.10、§9 阶段 6 验收第 12 条）。"""
from typing import Optional

from sqlmodel import Session, func, select

from app.models import AgentToolCallLog


def list_tool_logs(
    db: Session,
    tool_name: Optional[str],
    session_id: Optional[str],
    current: int,
    size: int,
) -> tuple[list[dict], int]:
    """工具调用日志分页查询，支持按 toolName / sessionId 筛选（管理端「助手日志」页）。"""
    stmt = select(AgentToolCallLog)
    count_stmt = select(func.count(AgentToolCallLog.id))
    if tool_name:
        stmt = stmt.where(AgentToolCallLog.tool_name == tool_name)
        count_stmt = count_stmt.where(AgentToolCallLog.tool_name == tool_name)
    if session_id:
        stmt = stmt.where(AgentToolCallLog.session_id == session_id)
        count_stmt = count_stmt.where(AgentToolCallLog.session_id == session_id)
    total = db.exec(count_stmt).one()
    rows = db.exec(stmt.order_by(AgentToolCallLog.id.desc()).offset((current - 1) * size).limit(size)).all()
    return [_to_vo(r) for r in rows], total


def _to_vo(r: AgentToolCallLog) -> dict:
    return {
        "id": r.id,
        "sessionId": r.session_id,
        "userId": r.user_id,
        "toolName": r.tool_name,
        "requestArgs": r.request_args,
        "responseData": r.response_data,
        "status": r.status,
        "costMs": r.cost_ms,
        "createTime": r.create_time.strftime("%Y-%m-%d %H:%M:%S"),
    }
