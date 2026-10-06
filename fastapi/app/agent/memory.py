"""智能体记忆机制（见施工规范 §6.5、§6.6、§6.10）。

三层记忆（缺一不可）：
  1. 当前身份注入 —— react.py 把「[当前旅行者ID=N]」拼进用户消息前缀
  2. 短时记忆 —— LangGraph MemorySaver（graph.py 按 thread_id 隔离）
  3. 长期记忆 —— MySQL agent_conversation 表（本文件负责落库/查询）

本文件还承载：会话标识生成、role 常量、待确认上下文（pending_book）缓存。
长期记忆的查询/写入接口在阶段 6.1 落地；本文件 6.0 先落 role 常量与 session_id 生成。
"""
import uuid

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


def generate_session_id() -> str:
    """前端首次传空，后端生成 uuid4 字符串并在返回体回传（§6.10）。"""
    return str(uuid.uuid4())
