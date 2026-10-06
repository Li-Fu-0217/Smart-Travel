"""智能体记忆机制（见施工规范 §6.5、§6.6、§6.10）。

三层记忆（缺一不可）：
  1. 当前身份注入 —— react.py 把「[当前旅行者ID=N]」拼进用户消息前缀
  2. 短时记忆 —— LangGraph MemorySaver（graph.py 按 thread_id 隔离）
  3. 长期记忆 —— MySQL agent_conversation 表（本文件负责落库/查询）

本文件还承载：会话标识生成、role 常量、待确认上下文（pending_book）双写缓存。
"""
import json
import uuid

from sqlmodel import Session, delete, select

from app.models import AgentConversation, FamilyMember, SysUser

# —— role 四值常量（§6.10：在代码里定义常量，禁止散落字符串）——
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
ROLE_SYSTEM = "system"
ROLE_PENDING_BOOK = "pending_book"

# 查询会话消息时只取这三种，过滤掉 pending_book（§6.10）
VISIBLE_ROLES = (ROLE_USER, ROLE_ASSISTANT, ROLE_SYSTEM)

# 会话列表：预览截前 80 字、最多 20 个（§6.10）
SESSION_PREVIEW_LEN = 80
MAX_SESSIONS = 20

# 待确认上下文进程内缓存：session_id -> pending dict（§6.6 双写，单进程 uvicorn 足够）
_PENDING_CACHE: dict[str, dict] = {}


def generate_session_id() -> str:
    """前端首次传空，后端生成 uuid4 字符串并在返回体回传（§6.10）。"""
    return str(uuid.uuid4())


def save_message(
    db: Session,
    user: SysUser,
    session_id: str,
    role: str,
    content: str | None,
    traveler_id: int | None = None,
) -> AgentConversation:
    """长期记忆落库（§6.5 第三层）。"""
    row = AgentConversation(
        user_id=user.id,
        traveler_id=traveler_id,
        session_id=session_id,
        role=role,
        content=content,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_messages(db: Session, user: SysUser, session_id: str) -> list[dict]:
    """查询会话消息，过滤掉 pending_book（§6.10）。"""
    rows = db.exec(
        select(AgentConversation)
        .where(AgentConversation.user_id == user.id, AgentConversation.session_id == session_id)
        .where(AgentConversation.role.in_(VISIBLE_ROLES))
        .order_by(AgentConversation.id)
    ).all()
    return [
        {"role": r.role, "content": r.content, "createTime": r.create_time.strftime("%Y-%m-%d %H:%M:%S")}
        for r in rows
    ]


def list_sessions(db: Session, user: SysUser) -> list[dict]:
    """会话列表：按 session_id 分组取最新一条预览，按最新倒序，最多 20，仅当前用户（§6.10）。"""
    rows = db.exec(
        select(AgentConversation)
        .where(AgentConversation.user_id == user.id)
        .where(AgentConversation.role.in_(VISIBLE_ROLES))
        .order_by(AgentConversation.id)
    ).all()
    grouped: dict[str, dict] = {}
    for r in rows:
        g = grouped.setdefault(r.session_id, {"first": r, "latest": r})
        g["latest"] = r  # 升序遍历，最后一条即最新
    sessions = []
    for sid, g in grouped.items():
        latest = g["latest"]
        sessions.append({
            "sessionId": sid,
            "travelerId": latest.traveler_id,
            "preview": (latest.content or "")[:SESSION_PREVIEW_LEN],
            "createTime": g["first"].create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "_latest": latest.create_time,
        })
    sessions.sort(key=lambda s: s["_latest"], reverse=True)
    for s in sessions:
        s.pop("_latest", None)
    return sessions[:MAX_SESSIONS]


def resolve_current_traveler(db: Session, user: SysUser, session_id: str | None = None) -> int | None:
    """解析「当前旅行者ID」：会话上下文 > 主绑定 > 任一绑定（§6.5 身份注入用）。"""
    if session_id:
        tid = db.exec(
            select(AgentConversation.traveler_id)
            .where(AgentConversation.session_id == session_id, AgentConversation.user_id == user.id)
            .where(AgentConversation.traveler_id.is_not(None))
            .order_by(AgentConversation.id.desc())
        ).first()
        if tid:
            return tid
    primary = db.exec(
        select(FamilyMember.traveler_id)
        .where(FamilyMember.user_id == user.id, FamilyMember.is_primary == 1)
    ).first()
    if primary:
        return primary
    return db.exec(
        select(FamilyMember.traveler_id).where(FamilyMember.user_id == user.id).order_by(FamilyMember.id)
    ).first()


# —— 待确认上下文（§6.6：落库 + 进程内缓存双写，清除时两边一起清）——
def set_pending(db: Session, user: SysUser, session_id: str, pending: dict) -> None:
    _PENDING_CACHE[session_id] = pending
    save_message(db, user, session_id, ROLE_PENDING_BOOK, json.dumps(pending, ensure_ascii=False))


def get_pending(db: Session, user: SysUser, session_id: str) -> dict | None:
    if session_id in _PENDING_CACHE:
        return _PENDING_CACHE[session_id]
    row = db.exec(
        select(AgentConversation.content)
        .where(
            AgentConversation.user_id == user.id,
            AgentConversation.session_id == session_id,
            AgentConversation.role == ROLE_PENDING_BOOK,
        )
        .order_by(AgentConversation.id.desc())
    ).first()
    if row:
        try:
            return json.loads(row)
        except (json.JSONDecodeError, TypeError):
            return None
    return None


def clear_pending(db: Session, user: SysUser, session_id: str) -> None:
    _PENDING_CACHE.pop(session_id, None)
    db.exec(
        delete(AgentConversation).where(
            AgentConversation.user_id == user.id,
            AgentConversation.session_id == session_id,
            AgentConversation.role == ROLE_PENDING_BOOK,
        )
    )
    db.commit()
