"""智能体编排图（见施工规范 §6.1、§6.7、§6.8、§6.11、§6.12）。

技术分工（§6.1）：LangGraph 承载 ReAct 状态图、检查点（MemorySaver）、步数上限、状态读取；
LangChain 仅提供标准件（ChatOpenAI / StructuredTool / 消息类型 / create_agent）。

本文件职责：
  - SYSTEM_PROMPT（§6.8）
  - build_agent()：create_agent(llm, tools, system_prompt=SYSTEM_PROMPT,
    middleware=[...], checkpointer=MemorySaver(), name="travel_react")
  - TravelAgentMiddleware（§6.11）：写库工具二次校验 + 每轮用量统计 + traveler_id 兜底
  - _extract_steps()：从消息轨迹还原「思考 → 行动 → 观察」步骤（§6.7）
  - ItineraryCard + extract_card()：行程卡片按需结构化抽取（§6.12）
"""
from __future__ import annotations

import json
import time

from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver

from app.agent.observation_format import format_observation
from app.agent.tools import (
    TOOL_BOOK_ITEM,
    TOOL_CHECK_TRIP_SCHEDULE,
    TOOL_COPY_TRIP_TEMPLATE,
    TOOL_DISTILL_PREFERENCES,
    TOOL_NOTIFY_COMPANIONS,
    TOOL_QUERY_TRAVELER_PROFILE,
    TOOL_RECOMMEND_ITINERARY,
    TOOL_SAVE_TRAVEL_RECORD,
    TOOL_TRIGGER_TRAVEL_ALERT,
)
from app.common.result import CamelModel

# 进程内短时记忆，按 thread_id 隔离（§6.1）；单进程 uvicorn 足够
_checkpointer = MemorySaver()

# 递归步数上限（§6.1 硬性护栏）
RECURSION_LIMIT = 12


# —— 系统提示词（§6.8：必须写清工具使用规则）——
SYSTEM_PROMPT = """你是「智能旅行助手」，通过调用工具为绑定旅行者的用户办理行程相关事务。

可用的 11 个工具与使用规则：
1. 涉及时效性/待办的问题，先调用 check_trip_schedule 查行程待办与逾期情况
2. 想预约必须先调用 query_available_booking 查可约时段，把可选时段告诉用户，等用户明确确认后再调用 book_item 下单
3. 预约成功后可调用 notify_companions 通知同行人
4. 用户明确表达求助、走失、身体不适、证件丢失等紧急情况时，调用 trigger_travel_alert 求助告警工具
5. 涉及签证政策、出行注意事项等常识问题，先调用 query_guide_knowledge 检索攻略库再回答
6. 回答用简洁中文，不要编造工具未返回的数据
7. 用排除法建立意图互斥：紧急意图只走告警工具；政策类问题只走知识库检索，不与预约链路混合
8. 用户想要行程推荐时，调用 recommend_itinerary（它基于偏好标签与历史记录）
9. 用户表达「记录一下去过哪/评价」时调用 save_travel_record；表达「总结/更新偏好」时调用 distill_preferences
10. 用户说「按模板复制成行程」时调用 copy_trip_template

需要 traveler_id 时，用消息前缀里标注的「当前旅行者ID」。"""


# —— 结构化输出模型（§6.12）——
class ItineraryDay(CamelModel):
    day_index: int
    title: str
    items: list[str] = []


class ItineraryCard(CamelModel):
    title: str
    destination: str
    day_count: int
    days: list[ItineraryDay] = []
    tags: list[str] = []
    tips: str | None = None


# 需要 traveler_id 的工具（敏感参数兜底补齐用，§6.11）
# 注：§6.11「写库类工具二次校验」仅在 book_item 上有明确闸门（须已存在待确认上下文，见 wrap_tool_call）。
# 其余 5 个写库工具被模型/规则链调用本身就是「用户意向明确」的信号，无额外可校验的意图信号，故不另设闸门。
_TRAVELER_TOOLS = {
    TOOL_QUERY_TRAVELER_PROFILE,
    TOOL_CHECK_TRIP_SCHEDULE,
    TOOL_BOOK_ITEM,
    TOOL_NOTIFY_COMPANIONS,
    TOOL_TRIGGER_TRAVEL_ALERT,
    TOOL_RECOMMEND_ITINERARY,
    TOOL_SAVE_TRAVEL_RECORD,
    TOOL_DISTILL_PREFERENCES,
    TOOL_COPY_TRIP_TEMPLATE,
}


class TravelAgentMiddleware(AgentMiddleware):
    """§6.11 中间件：承担三件事（仅模型编排路径生效；工具级埋点仍在 execute_tool）。"""

    def __init__(self, traveler_id: int | None = None, pending_getter=None):
        self.traveler_id = traveler_id
        self._pending_getter = pending_getter or (lambda: None)
        self.usage = {"tool_calls": 0, "total_ms": 0, "input_tokens": 0, "output_tokens": 0}
        self._t0: float | None = None

    # 1) 每轮用量统计：总耗时
    def before_agent(self, state, runtime) -> dict | None:
        self._t0 = time.perf_counter()
        return None

    def after_agent(self, state, runtime) -> dict | None:
        if self._t0 is not None:
            self.usage["total_ms"] = int((time.perf_counter() - self._t0) * 1000)
        return None

    # 2) 每轮用量统计：模型 token（能拿到就记）
    def after_model(self, state, runtime) -> dict | None:
        try:
            msgs = state.get("messages", []) if isinstance(state, dict) else getattr(state, "messages", [])
            if msgs:
                um = getattr(msgs[-1], "usage_metadata", None) or {}
                self.usage["input_tokens"] += int(um.get("input_tokens") or 0)
                self.usage["output_tokens"] += int(um.get("output_tokens") or 0)
        except Exception:  # noqa: BLE001 —— 统计失败不影响主流程
            pass
        return None

    # 3) 写库二次校验 + traveler_id 兜底 + 工具调用计数
    def wrap_tool_call(self, request, handler):
        tc = request.tool_call
        name = tc.get("name") or tc["name"]
        args = dict(tc.get("args") or {})
        self.usage["tool_calls"] += 1

        # 敏感参数兜底补齐：traveler_id 缺失时从会话上下文补全（§6.11）
        if name in _TRAVELER_TOOLS and not args.get("traveler_id") and self.traveler_id:
            args["traveler_id"] = self.traveler_id
            request = request.override(tool_call={**tc, "args": args})

        # 写库类工具二次校验：book_item 必须已存在待确认上下文，否则拦下、不落库（§6.11）
        if name == TOOL_BOOK_ITEM and not self._pending_getter():
            return ToolMessage(
                content=json.dumps(
                    {"error": "尚未取得用户对预约时段的明确确认，请先把可选时段展示给用户，等用户点选后再下单"},
                    ensure_ascii=False,
                ),
                tool_call_id=tc.get("id") or tc["id"],
                name=name,
            )
        return handler(request)


def build_agent(llm, tools, middleware: list[AgentMiddleware]):
    """用 create_agent 装配 ReAct 图（§6.1）。recursion_limit 在 invoke 的 config 里传。"""
    return create_agent(
        llm,
        tools,
        system_prompt=SYSTEM_PROMPT,
        middleware=middleware,
        checkpointer=_checkpointer,
        name="travel_react",
    )


def _extract_steps(messages: list[BaseMessage]) -> list[dict]:
    """从消息轨迹还原前端可展示的思考步骤（§6.7）。只解析最后一条 HumanMessage 之后的部分。"""
    steps: list[dict] = []
    round_no = 0
    start = 0
    for i in range(len(messages) - 1, -1, -1):
        if messages[i].__class__.__name__ == "HumanMessage":
            start = i + 1
            break

    for msg in messages[start:]:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                round_no += 1
                steps.append({
                    "round": round_no,
                    "thought": msg.content or f"调用工具 {tc['name']}",
                    "action": tc["name"],
                    "observation": "",
                })
        elif isinstance(msg, ToolMessage):
            brief = format_observation(str(msg.content), getattr(msg, "name", ""))
            for s in reversed(steps):
                if s.get("action") == getattr(msg, "name", None) and not s.get("observation"):
                    s["observation"] = brief
                    break
            else:
                if steps and not steps[-1].get("observation"):
                    steps[-1]["observation"] = brief
        elif isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
            round_no += 1
            steps.append({"round": round_no, "thought": "整理答复给您", "action": None, "observation": "已生成办理结果说明"})
    return steps


def _final_reply(messages: list[BaseMessage]) -> str:
    """最终回复取最后一条不含 tool_calls 的 AIMessage.content（§6.7）。"""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
            return str(msg.content)
    return ""


def extract_card(llm, context: str) -> ItineraryCard | None:
    """按需二次结构化抽取（§6.12）：仅当本轮轨迹含 recommend_itinerary / copy_trip_template 时调用。
    抽取失败返回 None，绝不让整轮对话失败。"""
    try:
        return llm.with_structured_output(ItineraryCard).invoke(context)
    except Exception:  # noqa: BLE001 —— 降级：纯文本回复照常返回
        return None
