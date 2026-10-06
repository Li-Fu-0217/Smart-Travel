"""智能体工具层（见施工规范 §6.2、§6.3、§6.11）。

铁律一：工具只是薄壳，业务在 service 层 —— handler 只做「参数整形 → 调 service → 返回数据」。
铁律二：所有工具经 execute_tool 统一埋点（agent_tool_call_log），异常不穿透到模型。
铁律三：原始 JSON 由 observation_format.format_observation 转人类可读中文（展示层，见 §6.7）。
工具名必须与 HANDLERS 字典 key 完全一致（字符串分发，写错即抛「未知工具」）。
"""
from __future__ import annotations

import json
import time
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Callable

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.common.constants import ALERT_TYPES
from app.common.exceptions import BusinessException
from app.models import AgentToolCallLog, SysUser
from app.schemas.alert import AlertCreateRequest
from app.schemas.booking import BookingOrderCreateRequest
from app.schemas.record import RecordCreateRequest
from app.schemas.template import TemplateCopyRequest
from app.services import (
    alert_service,
    booking_service,
    guide_service,
    notification_service,
    preference_service,
    recommend_service,
    record_service,
    template_service,
    traveler_service,
    trip_service,
)


# —— 工具名常量（与 tool_catalog.py 逐字对齐的唯一权威来源）——
TOOL_QUERY_TRAVELER_PROFILE = "query_traveler_profile"
TOOL_CHECK_TRIP_SCHEDULE = "check_trip_schedule"
TOOL_QUERY_AVAILABLE_BOOKING = "query_available_booking"
TOOL_BOOK_ITEM = "book_item"
TOOL_NOTIFY_COMPANIONS = "notify_companions"
TOOL_TRIGGER_TRAVEL_ALERT = "trigger_travel_alert"
TOOL_QUERY_GUIDE_KNOWLEDGE = "query_guide_knowledge"
TOOL_RECOMMEND_ITINERARY = "recommend_itinerary"
TOOL_SAVE_TRAVEL_RECORD = "save_travel_record"
TOOL_DISTILL_PREFERENCES = "distill_preferences"
TOOL_COPY_TRIP_TEMPLATE = "copy_trip_template"

TOOL_NAMES: tuple[str, ...] = (
    TOOL_QUERY_TRAVELER_PROFILE,
    TOOL_CHECK_TRIP_SCHEDULE,
    TOOL_QUERY_AVAILABLE_BOOKING,
    TOOL_BOOK_ITEM,
    TOOL_NOTIFY_COMPANIONS,
    TOOL_TRIGGER_TRAVEL_ALERT,
    TOOL_QUERY_GUIDE_KNOWLEDGE,
    TOOL_RECOMMEND_ITINERARY,
    TOOL_SAVE_TRAVEL_RECORD,
    TOOL_DISTILL_PREFERENCES,
    TOOL_COPY_TRIP_TEMPLATE,
)


# —— 各工具入参 schema（字段名与 tool_catalog.py 的 params 逐字对齐）——
class _QueryTravelerProfileArgs(BaseModel):
    traveler_id: int | None = Field(None, description="旅行者ID")


class _CheckTripScheduleArgs(BaseModel):
    traveler_id: int | None = Field(None, description="旅行者ID")


class _QueryAvailableBookingArgs(BaseModel):
    item_type: str | None = Field(None, description="预约项目类型：guide/homestay/experience/ticket，可空表示全部")
    days: int = Field(3, description="查询未来几天（1-30）")


class _BookItemArgs(BaseModel):
    traveler_id: int | None = Field(None, description="旅行者ID")
    catalog_id: int = Field(..., description="预约项目ID")
    slot: str = Field(..., description="预约时段，如 2026-03-12 09:00")
    guest_count: int = Field(1, description="人数")
    remark: str | None = Field(None, description="备注")


class _NotifyCompanionsArgs(BaseModel):
    traveler_id: int | None = Field(None, description="旅行者ID")
    message: str = Field(..., description="要通知的内容")


class _TriggerTravelAlertArgs(BaseModel):
    traveler_id: int | None = Field(None, description="旅行者ID")
    location: str | None = Field(None, description="当前位置")
    message: str | None = Field(None, description="求助说明")
    alert_type: str = Field("other", description="求助类型：lost/illness/document/accident/other")


class _QueryGuideKnowledgeArgs(BaseModel):
    query: str = Field(..., description="检索关键词或问题")


class _RecommendItineraryArgs(BaseModel):
    traveler_id: int | None = Field(None, description="旅行者ID")


class _SaveTravelRecordArgs(BaseModel):
    traveler_id: int | None = Field(None, description="旅行者ID")
    destination: str = Field(..., description="目的地")
    rating: int | None = Field(None, description="评分 1-5")
    content: str | None = Field(None, description="感受/评价")


class _DistillPreferencesArgs(BaseModel):
    traveler_id: int | None = Field(None, description="旅行者ID")


class _CopyTripTemplateArgs(BaseModel):
    traveler_id: int | None = Field(None, description="旅行者ID")
    template_id: int = Field(..., description="行程模板ID")
    start_date: str = Field(..., description="行程开始日期 YYYY-MM-DD")


ARGS_SCHEMAS: dict[str, type[BaseModel]] = {
    TOOL_QUERY_TRAVELER_PROFILE: _QueryTravelerProfileArgs,
    TOOL_CHECK_TRIP_SCHEDULE: _CheckTripScheduleArgs,
    TOOL_QUERY_AVAILABLE_BOOKING: _QueryAvailableBookingArgs,
    TOOL_BOOK_ITEM: _BookItemArgs,
    TOOL_NOTIFY_COMPANIONS: _NotifyCompanionsArgs,
    TOOL_TRIGGER_TRAVEL_ALERT: _TriggerTravelAlertArgs,
    TOOL_QUERY_GUIDE_KNOWLEDGE: _QueryGuideKnowledgeArgs,
    TOOL_RECOMMEND_ITINERARY: _RecommendItineraryArgs,
    TOOL_SAVE_TRAVEL_RECORD: _SaveTravelRecordArgs,
    TOOL_DISTILL_PREFERENCES: _DistillPreferencesArgs,
    TOOL_COPY_TRIP_TEMPLATE: _CopyTripTemplateArgs,
}


def _get_traveler_id(args: dict) -> int:
    """traveler_id 缺省时由身份注入/中间件补齐；这里兜底给可读错误。"""
    tid = args.get("traveler_id")
    if tid is None:
        raise BusinessException("缺少旅行者ID（traveler_id），请先绑定家人档案", code=400)
    return int(tid)


# —— 工具 handler（铁律一：只整形参数 + 调 service + 返回数据）——
def _query_traveler_profile(db: Session, user: SysUser, args: dict) -> dict:
    tid = _get_traveler_id(args)
    profile = traveler_service.get_profile(db, user, tid)
    today = trip_service.today(db, user, tid)
    return {
        "traveler_id": profile.id,
        "name": profile.name,
        "preferences": profile.preferences,
        "preference_tags": profile.preference_tags,
        "dietary_restrictions": profile.dietary_restrictions,
        "allergies": profile.allergies,
        "mobility_notes": profile.mobility_notes,
        "overdue_todos": [t.item_name for t in today.overdue_todos],
    }


def _check_trip_schedule(db: Session, user: SysUser, args: dict) -> dict:
    tid = _get_traveler_id(args)
    today = trip_service.today(db, user, tid)
    return {
        "traveler_id": tid,
        "today_todos": [t.item_name for t in today.today_todos],
        "overdue_todos": [{"item_name": t.item_name, "due_time": t.due_time} for t in today.overdue_todos],
        "next_days": [{"date": d.date, "items": d.items} for d in today.next_days],
    }


def _query_available_booking(db: Session, user: SysUser, args: dict) -> list:
    return booking_service.slots(db, args.get("item_type"), int(args.get("days", 3)))


def _book_item(db: Session, user: SysUser, args: dict):
    tid = _get_traveler_id(args)
    payload = BookingOrderCreateRequest(
        traveler_id=tid,
        catalog_id=int(args["catalog_id"]),
        slot=args["slot"],
        guest_count=int(args.get("guest_count", 1)),
        remark=args.get("remark"),
    )
    # 工具层显式 source="agent"；人工下单仍走默认 "manual"（§5.8）
    return booking_service.create_order(db, user, payload, source="agent")


def _notify_companions(db: Session, user: SysUser, args: dict) -> dict:
    tid = _get_traveler_id(args)
    return notification_service.notify_companions(db, tid, args["message"], source="agent")


def _trigger_travel_alert(db: Session, user: SysUser, args: dict):
    tid = _get_traveler_id(args)
    alert_type = args.get("alert_type") or "other"
    if alert_type not in ALERT_TYPES:
        alert_type = "other"
    payload = AlertCreateRequest(
        traveler_id=tid,
        location=args.get("location"),
        message=args.get("message"),
        alert_type=alert_type,
        notify_family=1,   # 通知紧急联系人（绑定家人）
        notify_staff=0,
        source="agent",
    )
    return alert_service.create_sos(db, user, payload)


def _query_guide_knowledge(db: Session, user: SysUser, args: dict):
    return guide_service.query(db, args["query"])


def _recommend_itinerary(db: Session, user: SysUser, args: dict) -> dict:
    tid = _get_traveler_id(args)
    return recommend_service.recommend(db, user, tid)


def _save_travel_record(db: Session, user: SysUser, args: dict):
    tid = _get_traveler_id(args)
    payload = RecordCreateRequest(
        traveler_id=tid,
        destination=args.get("destination"),
        rating=args.get("rating"),
        content=args.get("content"),
    )
    return record_service.create_record(db, user, payload)


def _distill_preferences(db: Session, user: SysUser, args: dict):
    tid = _get_traveler_id(args)
    return preference_service.distill(db, user, tid)


def _copy_trip_template(db: Session, user: SysUser, args: dict):
    tid = _get_traveler_id(args)
    payload = TemplateCopyRequest(traveler_id=tid, start_date=date.fromisoformat(args["start_date"]))
    return template_service.copy_template(db, user, int(args["template_id"]), payload)


HANDLERS: dict[str, Callable[[Session, SysUser, dict], Any]] = {
    TOOL_QUERY_TRAVELER_PROFILE: _query_traveler_profile,
    TOOL_CHECK_TRIP_SCHEDULE: _check_trip_schedule,
    TOOL_QUERY_AVAILABLE_BOOKING: _query_available_booking,
    TOOL_BOOK_ITEM: _book_item,
    TOOL_NOTIFY_COMPANIONS: _notify_companions,
    TOOL_TRIGGER_TRAVEL_ALERT: _trigger_travel_alert,
    TOOL_QUERY_GUIDE_KNOWLEDGE: _query_guide_knowledge,
    TOOL_RECOMMEND_ITINERARY: _recommend_itinerary,
    TOOL_SAVE_TRAVEL_RECORD: _save_travel_record,
    TOOL_DISTILL_PREFERENCES: _distill_preferences,
    TOOL_COPY_TRIP_TEMPLATE: _copy_trip_template,
}


def _dispatch(db: Session, user: SysUser, tool_name: str, args: dict) -> Any:
    handler = HANDLERS.get(tool_name)
    if handler is None:
        raise ValueError(f"未知工具: {tool_name}")
    return handler(db, user, args or {})


def _to_jsonable(value: Any) -> Any:
    """把 VO / datetime / Decimal 递归转成可 json 序列化的结构。"""
    if isinstance(value, BaseModel):
        return _to_jsonable(value.model_dump(mode="python"))
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    return value


def execute_tool(db: Session, user: SysUser, tool_name: str, args: dict, *, session_id: str) -> dict:
    """统一埋点分发（铁律二）：无论成败都落一条 agent_tool_call_log；异常不穿透。"""
    start = time.perf_counter()
    status = 1
    try:
        result = _dispatch(db, user, tool_name, args)
        payload = _to_jsonable(result)
    except Exception as exc:  # noqa: BLE001 —— 异常不抛出，转为结构化返回
        status = 0
        payload = {"error": str(exc)}
    cost_ms = int((time.perf_counter() - start) * 1000)
    db.add(AgentToolCallLog(
        session_id=session_id,
        user_id=user.id or 0,
        tool_name=tool_name,
        request_args=json.dumps(_to_jsonable(args), ensure_ascii=False),
        response_data=json.dumps(payload, ensure_ascii=False)[:8000],  # 必须截断（§6.3）
        status=status,
        cost_ms=cost_ms,
        create_time=datetime.now(),
    ))
    db.commit()
    return {"ok": status == 1, "data": payload, "cost_ms": cost_ms}


# —— 各工具对模型的描述（§6.8 系统提示词与工具自身描述共同约束调用规则）——
_TOOL_DESCRIPTIONS: dict[str, str] = {
    TOOL_QUERY_TRAVELER_PROFILE: "查询旅行者档案：出行偏好、忌口、过敏、行动不便说明，以及近期逾期待办概况。需要了解某位家人的偏好或身体状况时使用。",
    TOOL_CHECK_TRIP_SCHEDULE: "查询某位旅行者的行程待办（签证/保险/接送机等）及逾期情况。涉及时效性/待办/逾期的问题先查这里。",
    TOOL_QUERY_AVAILABLE_BOOKING: "按项目类型查询可预约项目与未来可用时段。想预约前必须先查这里，把可选时段告诉用户。",
    TOOL_BOOK_ITEM: "为旅行者提交预约订单（source=agent）。必须先取得用户明确确认（点选时段）后才能调用。",
    TOOL_NOTIFY_COMPANIONS: "向该旅行者的绑定联系人发送站内消息。预约成功或需要提醒同行人时使用。",
    TOOL_TRIGGER_TRAVEL_ALERT: "创建旅途求助工单并通知紧急联系人。用户明确表达求助/走失/身体不适/证件丢失时使用。",
    TOOL_QUERY_GUIDE_KNOWLEDGE: "RAG 检索攻略库（签证政策、目的地指南、出行注意事项）。涉及签证政策等常识问题先检索再回答。",
    TOOL_RECOMMEND_ITINERARY: "根据旅行者偏好与历史旅游记录，推荐行程方案。用户想要行程推荐时使用。",
    TOOL_SAVE_TRAVEL_RECORD: "为旅行者写入一条旅游记录（目的地、评分、感受）。用户说「记录一下去过哪/评价」时使用。",
    TOOL_DISTILL_PREFERENCES: "从该旅行者的历史旅游记录中提炼偏好标签，回写到档案。用户想更新/总结偏好时使用。",
    TOOL_COPY_TRIP_TEMPLATE: "把某个行程模板复制成该旅行者的一份新行程（含日程明细）。用户说「按模板复制成行程」时使用。",
}


def build_tools(db: Session, user: SysUser, session_id: str) -> list[StructuredTool]:
    """为一次请求构建绑定 db/user/session_id 的工具列表（模型编排与规则编排共用 execute_tool）。"""
    tools: list[StructuredTool] = []
    for name in TOOL_NAMES:
        schema = ARGS_SCHEMAS[name]
        description = _TOOL_DESCRIPTIONS[name]

        def make(name: str = name, schema: type[BaseModel] = schema, description: str = description) -> StructuredTool:
            def _run(**kwargs: Any) -> str:
                result = execute_tool(db, user, name, kwargs, session_id=session_id)
                return json.dumps(result["data"], ensure_ascii=False)

            return StructuredTool.from_function(func=_run, name=name, description=description, args_schema=schema)

        tools.append(make())
    return tools
