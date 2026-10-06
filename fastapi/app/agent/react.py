"""智能体入口（见施工规范 §6.4、§6.5、§6.6、§6.12）。

三条路径（双模式 + 异常降级）：
  - 模型编排：已配置有效 LLM_API_KEY 且 AGENT_DEMO_MODE=false → LangGraph ReAct（graph.py）
  - 规则编排（默认）：未配置 Key 或 AGENT_DEMO_MODE=true → 按关键词规则选工具，仍真实写库
  - 异常降级：模型编排抛异常 → 回退规则编排 + 友好提示

本文件职责：模式选择、身份注入、关键词意图分类（含互斥消解）、组合链路、待确认时段匹配、卡片触发。
"""
from __future__ import annotations

import json
import logging
import re
from datetime import date, timedelta
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from sqlmodel import Session

from app.agent import graph, memory
from app.agent.memory import ROLE_ASSISTANT, ROLE_SYSTEM, ROLE_USER
from app.agent.observation_format import format_observation
from app.agent.tools import (
    TOOL_COPY_TRIP_TEMPLATE,
    TOOL_QUERY_AVAILABLE_BOOKING,
    TOOL_RECOMMEND_ITINERARY,
    build_tools,
    execute_tool,
)
from app.core.config import settings
from app.models import SysUser
from app.services import template_service

logger = logging.getLogger("travel_assistant.agent")

# —— 规则编排关键词分类（§6.4）：每类至少覆盖下列触发词 ——
INTENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "emergency": ("求助", "走散", "丢失", "身体不适", "急救", "报警", "晕倒"),
    "guide": ("签证", "攻略", "政策", "注意事项", "怎么办", "能带", "免签"),
    "todo": ("签证", "保险", "清单", "待办", "逾期", "没办", "忘了"),
    "booking": ("预约", "门票", "导游", "民宿", "体验", "订"),
    "booking_confirm": ("确认", "就这个", "可以", "好的"),
    "record": ("记录", "去过", "评价", "打个分"),
    "template": ("模板", "复制", "套用", "参考别人的行程", "行程广场"),
    "preference": ("我的偏好", "我喜欢", "口味", "更新偏好", "总结一下我的喜好"),
}

# 动作词（§6.4 待办意图优先）
_TODO_ACTION_WORDS = ("没办", "忘了", "逾期", "清单", "待办", "准备")
# 咨询词（§6.4 攻略意图判定，需排除预约/逾期类）
_GUIDE_CONSULT_WORDS = ("签证", "政策", "怎么办", "能带", "注意事项")
_GUIDE_EXCLUDE_WORDS = ("预约", "门票", "导游", "民宿", "逾期", "没办", "忘了")

# 待确认时段匹配顺序（§6.4）
_DATETIME_RE = re.compile(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})")

# 推荐意图触发词（§6.4「记录 → 偏好 → 推荐」链路）
_RECOMMEND_WORDS = ("推荐", "下次去哪", "去哪儿", "帮我规划", "行程推荐")


def _build_llm() -> ChatOpenAI:
    """按 §6.1 构建模型抽象（DeepSeek 兼容 OpenAI 协议）。"""
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=settings.LLM_MAX_TOKENS,
    )


# =====================================================================
# 规则编排（demo 模式）
# =====================================================================

def _has_any(text: str, words: tuple[str, ...] | list[str]) -> bool:
    return any(w in text for w in words)


def _is_emergency(text: str) -> bool:
    return _has_any(text, INTENT_KEYWORDS["emergency"])


def _is_guide(text: str) -> bool:
    has_consult = _has_any(text, _GUIDE_CONSULT_WORDS)
    has_exclude = _has_any(text, _GUIDE_EXCLUDE_WORDS)
    has_action = _has_any(text, _TODO_ACTION_WORDS)
    return has_consult and not has_exclude and not has_action


def _is_confirm(text: str) -> bool:
    return bool(_DATETIME_RE.search(text)) or _has_any(text, INTENT_KEYWORDS["booking_confirm"]) or "第一个" in text or "第二个" in text or "就约" in text


def _is_recommend(text: str) -> bool:
    return _has_any(text, _RECOMMEND_WORDS) or _has_any(text, INTENT_KEYWORDS["preference"])


def _match_slot(text: str, options: list[str]) -> str | None:
    """待确认时段匹配（§6.4）：精确包含 → 正则日期时间 → 序数词 → 兜底取第一个。"""
    norm = text.replace(" ", "")
    for o in options:
        if o.replace(" ", "") in norm:
            return o
    m = _DATETIME_RE.search(text)
    if m:
        return m.group(1)
    if "第二" in text:
        return options[1] if len(options) > 1 else None
    if "第一" in text or "就这个" in text or "就约这个" in text:
        return options[0] if options else None
    if _is_confirm(text):
        return options[0] if options else None
    return None


def _run_tool(db: Session, user: SysUser, session_id: str, tool_name: str, args: dict, steps: list[dict], thought: str) -> dict:
    """执行工具并追加一步「思考 → 行动 → 观察」（observation 走 format_observation，无 JSON）。"""
    result = execute_tool(db, user, tool_name, args, session_id=session_id)
    steps.append({
        "round": len(steps) + 1,
        "thought": thought,
        "action": tool_name,
        "observation": format_observation(result["data"], tool_name),
    })
    return result


def _first_catalog_pending(data: Any) -> dict | None:
    """从 query_available_booking 返回值里取第一个项目，构造待确认上下文（§6.6）。"""
    items = data if isinstance(data, list) else []
    for it in items:
        slots = it.get("slots") or []
        if slots:
            return {
                "type": "book_item",
                "catalogId": it.get("catalog_id"),
                "catalogName": it.get("catalog_name"),
                "options": slots[:4],
            }
    return None


def _demo_emergency(db: Session, user: SysUser, session_id: str, traveler_id: int | None, text: str) -> dict:
    steps: list[dict] = []
    r = _run_tool(db, user, session_id, "trigger_travel_alert", {
        "traveler_id": traveler_id, "message": text, "alert_type": "lost",
    }, steps, "检测到紧急求助意图，登记旅途求助")
    return {"reply": format_observation(r["data"], "trigger_travel_alert"), "steps": steps, "pending": None, "card": None}


def _demo_guide(db: Session, user: SysUser, session_id: str, traveler_id: int | None, text: str) -> dict:
    steps: list[dict] = []
    r = _run_tool(db, user, session_id, "query_guide_knowledge", {"query": text}, steps, "检索攻略库")
    return {"reply": format_observation(r["data"], "query_guide_knowledge"), "steps": steps, "pending": None, "card": None}


def _demo_confirm_booking(db: Session, user: SysUser, session_id: str, traveler_id: int | None, text: str, pending: dict) -> dict:
    steps: list[dict] = []
    slot = _match_slot(text, pending.get("options") or [])
    if slot is None:
        return {"reply": "当前没有可确认的预约时段，您可以稍后再试或前往预约中心手动选择", "steps": steps, "pending": pending, "card": None}
    r = _run_tool(db, user, session_id, "book_item", {
        "traveler_id": traveler_id, "catalog_id": pending["catalogId"], "slot": slot, "guest_count": 1,
    }, steps, f"用户选定时段 {slot}，提交预约订单")
    if r["ok"]:
        _run_tool(db, user, session_id, "notify_companions", {
            "traveler_id": traveler_id, "message": f"已为家人预约「{pending.get('catalogName')}」{slot}",
        }, steps, "预约成功，通知同行人")
        memory.clear_pending(db, user, session_id)
        return {"reply": format_observation(r["data"], "book_item"), "steps": steps, "pending": None, "card": None}
    # 预约失败：保留 pending，提示换时段（§6.4）
    return {"reply": format_observation(r["data"], "book_item"), "steps": steps, "pending": pending, "card": None}


def _demo_recommend(db: Session, user: SysUser, session_id: str, traveler_id: int | None, text: str) -> dict:
    steps: list[dict] = []
    _run_tool(db, user, session_id, "query_traveler_profile", {"traveler_id": traveler_id}, steps, "读取旅行者档案与现有偏好")
    _run_tool(db, user, session_id, "distill_preferences", {"traveler_id": traveler_id}, steps, "从历史记录提炼偏好并回写档案")
    r = _run_tool(db, user, session_id, "recommend_itinerary", {"traveler_id": traveler_id}, steps, "基于偏好与记录生成行程推荐")
    card = graph.ItineraryCard(**r["data"]) if r["ok"] else None
    reply = format_observation(r["data"], "recommend_itinerary") + "。您可以让我「按这个复制成行程」，或直接预约当地体验。"
    return {"reply": reply, "steps": steps, "pending": None, "card": card}


def _demo_template(db: Session, user: SysUser, session_id: str, traveler_id: int | None, text: str) -> dict:
    steps: list[dict] = []
    templates = template_service.list_templates(db)
    if not templates:
        return {"reply": "当前没有可复制的行程模板", "steps": steps, "pending": None, "card": None}
    tpl = templates[0]
    start_date = (date.today() + timedelta(days=7)).isoformat()
    r = _run_tool(db, user, session_id, "copy_trip_template", {
        "traveler_id": traveler_id, "template_id": tpl.id, "start_date": start_date,
    }, steps, f"按「{tpl.title}」模板复制生成行程")
    card = graph.ItineraryCard(title=tpl.title, destination=tpl.destination, day_count=tpl.day_count, days=[], tags=[], tips="已按模板复制为您的行程") if r["ok"] else None
    return {"reply": format_observation(r["data"], "copy_trip_template"), "steps": steps, "pending": None, "card": card}


def _demo_record(db: Session, user: SysUser, session_id: str, traveler_id: int | None, text: str) -> dict:
    steps: list[dict] = []
    destination = "目的地"
    # 从文本里粗提目的地：去 XX / 到了 XX
    m = re.search(r"去了?([一-龥]{2,6})", text)
    if m:
        destination = m.group(1)
    r = _run_tool(db, user, session_id, "save_travel_record", {
        "traveler_id": traveler_id, "destination": destination, "rating": 5, "content": text,
    }, steps, "记录一条旅游经历")
    return {"reply": format_observation(r["data"], "save_travel_record"), "steps": steps, "pending": None, "card": None}


def _demo_todo_booking(db: Session, user: SysUser, session_id: str, traveler_id: int | None, text: str) -> dict:
    """默认组合链路：查待办 → 通知同行人 → 查可约时段 → 待确认（§6.4）。"""
    steps: list[dict] = []
    r1 = _run_tool(db, user, session_id, "check_trip_schedule", {"traveler_id": traveler_id}, steps, "查询行程待办与逾期情况")
    overdue = (r1["data"].get("overdue_todos") or []) if r1["ok"] else []
    if overdue:
        _run_tool(db, user, session_id, "notify_companions", {
            "traveler_id": traveler_id, "message": "有行程待办已逾期，请注意办理",
        }, steps, "把逾期情况告知同行人")
    r3 = _run_tool(db, user, session_id, "query_available_booking", {"item_type": "experience"}, steps, "查询当地体验的可约时段")
    pending = _first_catalog_pending(r3["data"]) if r3["ok"] else None
    if pending:
        memory.set_pending(db, user, session_id, pending)
        steps.append({"round": len(steps) + 1, "thought": "整理可选时段，等您确认", "action": None, "observation": "已列出可选时段，请点选确认"})
        reply = f"这是「{pending['catalogName']}」的可选时段，请点选确认：{'、'.join(pending['options'])}"
        return {"reply": reply, "steps": steps, "pending": pending, "card": None}
    return {"reply": format_observation(r3["data"], "query_available_booking"), "steps": steps, "pending": None, "card": None}


def _run_demo(db: Session, user: SysUser, session_id: str, traveler_id: int | None, text: str) -> dict:
    pending = memory.get_pending(db, user, session_id)
    if _is_emergency(text):
        return _demo_emergency(db, user, session_id, traveler_id, text)
    if pending and _is_confirm(text):
        return _demo_confirm_booking(db, user, session_id, traveler_id, text, pending)
    if _is_guide(text):
        return _demo_guide(db, user, session_id, traveler_id, text)
    if _is_recommend(text):
        return _demo_recommend(db, user, session_id, traveler_id, text)
    if _has_any(text, INTENT_KEYWORDS["template"]):
        return _demo_template(db, user, session_id, traveler_id, text)
    if _has_any(text, INTENT_KEYWORDS["record"]):
        return _demo_record(db, user, session_id, traveler_id, text)
    return _demo_todo_booking(db, user, session_id, traveler_id, text)


# =====================================================================
# 模型编排（LangGraph ReAct）
# =====================================================================

def _model_history_messages(db: Session, user: SysUser, session_id: str, exclude_last: bool) -> list:
    """长期记忆转模型消息（§6.5 第三层，最多注入最近 20 条）。"""
    history = memory.list_messages(db, user, session_id)
    if exclude_last:
        history = history[:-1]
    history = history[-20:]
    out: list = []
    for h in history:
        if h["role"] == ROLE_USER:
            out.append(HumanMessage(content=h["content"]))
        elif h["role"] == ROLE_SYSTEM:
            out.append(SystemMessage(content=h["content"]))
        else:
            out.append(AIMessage(content=h["content"]))
    return out


def _run_model(db: Session, user: SysUser, session_id: str, traveler_id: int | None, injected: str) -> dict:
    llm = _build_llm()
    tools = build_tools(db, user, session_id)
    mw = graph.TravelAgentMiddleware(traveler_id=traveler_id, pending_getter=lambda: memory.get_pending(db, user, session_id))
    agent = graph.build_agent(llm, tools, [mw])
    config = {"configurable": {"thread_id": f"u{user.id}:{session_id}"}, "recursion_limit": graph.RECURSION_LIMIT}

    # 去重（§6.5）：先问检查点是否已有状态
    state = agent.get_state(config)
    has_checkpoint = bool(state.values.get("messages")) if state and state.values else False
    if has_checkpoint:
        invoke_input = {"messages": [HumanMessage(content=injected)]}
    else:
        invoke_input = {"messages": _model_history_messages(db, user, session_id, exclude_last=True) + [HumanMessage(content=injected)]}

    result = agent.invoke(invoke_input, config=config)
    messages = result.get("messages", [])
    steps = graph._extract_steps(messages)
    reply = graph._final_reply(messages)

    used = {getattr(m, "name", "") for m in messages if isinstance(m, ToolMessage)}
    card = None
    if TOOL_RECOMMEND_ITINERARY in used or TOOL_COPY_TRIP_TEMPLATE in used:
        context = "\n".join(str(m.content) for m in messages if isinstance(m, ToolMessage)) + "\n\n" + reply
        card = graph.extract_card(llm, context)

    pending = None
    if TOOL_QUERY_AVAILABLE_BOOKING in used:
        for m in messages:
            if isinstance(m, ToolMessage) and getattr(m, "name", "") == TOOL_QUERY_AVAILABLE_BOOKING:
                try:
                    data = json.loads(str(m.content))
                except (json.JSONDecodeError, TypeError):
                    data = None
                p = _first_catalog_pending(data)
                if p:
                    memory.set_pending(db, user, session_id, p)
                    pending = p
                break
    return {"reply": reply, "steps": steps, "pending": pending, "card": card, "usage": mw.usage}


# =====================================================================
# 入口
# =====================================================================

def _inject_identity(message: str, traveler_id: int | None) -> str:
    """当前身份注入（§6.5 第一层）：把「当前旅行者ID=N」拼进用户消息前缀。"""
    return f"[当前旅行者ID={traveler_id}]\n{message}" if traveler_id else message


def chat(db: Session, user: SysUser, message: str, session_id: str | None) -> dict:
    """助手入口：返回 sessionId/reply/steps/pendingConfirm/demoMode/engine/card。"""
    if not session_id:
        session_id = memory.generate_session_id()
    traveler_id = memory.resolve_current_traveler(db, user, session_id)
    demo_mode = settings.AGENT_DEMO_MODE or not settings.LLM_API_KEY

    memory.save_message(db, user, session_id, ROLE_USER, message, traveler_id)
    injected = _inject_identity(message, traveler_id)

    if demo_mode:
        out = _run_demo(db, user, session_id, traveler_id, message)
        engine = "demo"
    else:
        try:
            out = _run_model(db, user, session_id, traveler_id, injected)
            engine = "langgraph"
        except Exception:  # noqa: BLE001 —— 异常降级（§6.4），不出现 500
            logger.exception("模型编排失败，降级为规则编排 session=%s", session_id)
            out = _run_demo(db, user, session_id, traveler_id, message)
            out["reply"] = "刚才智能编排暂时不可用，已切换为本地助手继续为您办理。\n\n" + out["reply"]
            engine = "demo"

    memory.save_message(db, user, session_id, ROLE_ASSISTANT, out["reply"], traveler_id)
    card = out.get("card")
    return {
        "session_id": session_id,
        "reply": out["reply"],
        "steps": out["steps"],
        "pending_confirm": out.get("pending"),
        "demo_mode": engine == "demo",
        "engine": engine,
        "card": card.model_dump(by_alias=True) if card is not None else None,
    }
