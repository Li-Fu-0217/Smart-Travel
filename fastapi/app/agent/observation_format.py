"""工具返回值的人类可读中文格式化（见施工规范 §6.3 铁律三、§6.7）。

原始 JSON 严禁直接展示给用户。本模块把各工具的返回值翻译成自然语言摘要，用于：
  - 前端「思考步骤」里 observation 一栏（§6.7）
  - 兼容 snake_case / camelCase 两套字段名；状态码映射中文；时间 YYYY-MM-DD HH:MM
兜底：遇到无法识别的结构，抽取常见中文字段，绝不回退打印 JSON。
"""
import json
from typing import Any

from app.agent import tools

# 状态码 → 中文（§6.3）
_STATUS_CN = {
    "pending": "待确认", "confirmed": "已确认", "cancelled": "已取消", "done": "已完成",
    "open": "待处理", "handling": "处理中", "closed": "已关闭",
    "registered": "已报名", "completed": "已完成",
}

# 预约失败 → 可操作提示（§6.4）
_ERROR_HINTS: tuple[tuple[str, str], ...] = (
    ("已被预约", "该时段刚被他人预约，请换一个时段"),
    ("刚被他人", "该时段刚被他人预约，请换一个时段"),
    ("不存在", "所选项目暂不可用，请重新选择"),
    ("下架", "所选项目暂不可用，请重新选择"),
    ("version", "该预约刚被修改，请刷新后重试"),
)


def _parse(content: str) -> Any:
    if isinstance(content, (dict, list)):
        return content
    try:
        return json.loads(content) if content else {}
    except (json.JSONDecodeError, TypeError):
        return {"_raw": content}


def _get(obj: Any, *keys: str) -> Any:
    """按多个候选 key 取值（兼容 snake_case / camelCase）。"""
    if isinstance(obj, dict):
        for k in keys:
            if k in obj and obj[k] is not None:
                return obj[k]
    return None


def _fmt_time(v: Any) -> str:
    if v is None:
        return ""
    s = str(v)
    return s[:16] if len(s) >= 16 else s


def _status_cn(v: Any) -> str:
    return _STATUS_CN.get(str(v), str(v) if v else "")


def _format_error(msg: str) -> str:
    for key, hint in _ERROR_HINTS:
        if key in msg:
            return hint
    return f"办理未成功：{msg}"


def _f_profile(d: dict) -> str:
    name = _get(d, "name") or "旅行者"
    parts = [str(name)]
    tags = _get(d, "preference_tags")
    if tags:
        parts.append(f"偏好：{tags}")
    if _get(d, "dietary_restrictions"):
        parts.append(f"忌口：{d.get('dietary_restrictions')}")
    if _get(d, "allergies"):
        parts.append(f"过敏：{d.get('allergies')}")
    overdue = _get(d, "overdue_todos") or []
    if overdue:
        parts.append(f"逾期 {len(overdue)} 项（{'、'.join(str(x) for x in overdue[:3])}）")
    return "，".join(parts)


def _f_schedule(d: dict) -> str:
    today = _get(d, "today_todos") or []
    overdue = _get(d, "overdue_todos") or []
    parts = []
    if overdue:
        names = "、".join(_get(o, "item_name") or str(o) for o in overdue[:3])
        parts.append(f"逾期待办：{names}")
    if today:
        parts.append(f"今日待办 {len(today)} 项")
    if not parts:
        parts.append("暂无待办")
    return "行程待办：" + "；".join(parts)


def _f_slots(d: Any) -> str:
    items = d if isinstance(d, list) else []
    if not items:
        return "暂无可约时段"
    parts = []
    for it in items[:3]:
        name = _get(it, "catalog_name", "catalogName") or "项目"
        slots = _get(it, "slots") or []
        sample = "、".join(_fmt_time(s) for s in slots[:3])
        more = f" 等共 {len(slots)} 个" if len(slots) > 3 else f" 共 {len(slots)} 个"
        parts.append(f"「{name}」可约：{sample}{more}")
    return "；".join(parts)


def _f_book(d: dict) -> str:
    name = _get(d, "catalog_name", "catalogName") or "项目"
    slot = _get(d, "slot")
    status = _status_cn(_get(d, "status"))
    traveler = _get(d, "traveler_name", "travelerName") or ""
    parts = [f"已预约「{name}」"]
    if traveler:
        parts.append(f"服务对象：{traveler}")
    if slot:
        parts.append(f"时间：{_fmt_time(slot)}")
    if status:
        parts.append(f"状态：{status}")
    return "；".join(parts)


def _f_notify(d: dict) -> str:
    n = _get(d, "notified_count") or 0
    return f"已向 {n} 位同行人发送站内消息"


def _f_alert(d: dict) -> str:
    name = _get(d, "traveler_name", "travelerName") or "家人"
    status = _status_cn(_get(d, "status"))
    msg = _get(d, "message", "location") or "已登记求助"
    return f"已为 {name} 登记旅途求助（{status}）：{msg}"


def _f_guide(d: dict) -> str:
    results = _get(d, "results") or []
    if not results:
        return _get(d, "message") or "攻略库暂未检索到很贴切的内容"
    first = results[0]
    content = (_get(first, "content") or "")[:100]  # 单条截 100 字（§6.3）
    title = _get(first, "title")
    head = f"《{title}》" if title else "例如"
    return f"检索到 {len(results)} 条相关说明，{head}：{content}"


def _f_recommend(d: dict) -> str:
    title = _get(d, "title") or "行程推荐"
    destination = _get(d, "destination") or ""
    days = _get(d, "day_count") or len(_get(d, "days") or [])
    tags = _get(d, "tags") or []
    parts = [f"为您推荐「{title}」"]
    if destination:
        parts.append(f"目的地：{destination}")
    if days:
        parts.append(f"共 {days} 天")
    if tags:
        parts.append(f"偏好：{'、'.join(tags)}")
    return "，".join(parts)


def _f_record(d: dict) -> str:
    destination = _get(d, "destination") or "目的地"
    rating = _get(d, "rating")
    rating_txt = f"，评分 {rating} 星" if rating else ""
    return f"已记录旅游经历：{destination}{rating_txt}"


def _f_distill(d: dict) -> str:
    tags = _get(d, "preference_tags") or ""
    summary = _get(d, "preference_summary") or ""
    parts = ["已更新旅行偏好"]
    if tags:
        parts.append(f"标签：{tags}")
    if summary:
        parts.append(f"摘要：{summary}")
    return "；".join(parts)


def _f_copy(d: dict) -> str:
    title = _get(d, "title") or "模板"
    trip_id = _get(d, "id")
    start = _get(d, "start_date")
    end = _get(d, "end_date")
    parts = [f"已按「{title}」模板创建行程"]
    if trip_id is not None:
        parts.append(f"行程ID {trip_id}")
    if start and end:
        parts.append(f"起止 {_fmt_time(start)[:10]} ~ {_fmt_time(end)[:10]}")
    return "，".join(parts)


_FORMATTERS = {
    tools.TOOL_QUERY_TRAVELER_PROFILE: _f_profile,
    tools.TOOL_CHECK_TRIP_SCHEDULE: _f_schedule,
    tools.TOOL_QUERY_AVAILABLE_BOOKING: _f_slots,
    tools.TOOL_BOOK_ITEM: _f_book,
    tools.TOOL_NOTIFY_COMPANIONS: _f_notify,
    tools.TOOL_TRIGGER_TRAVEL_ALERT: _f_alert,
    tools.TOOL_QUERY_GUIDE_KNOWLEDGE: _f_guide,
    tools.TOOL_RECOMMEND_ITINERARY: _f_recommend,
    tools.TOOL_SAVE_TRAVEL_RECORD: _f_record,
    tools.TOOL_DISTILL_PREFERENCES: _f_distill,
    tools.TOOL_COPY_TRIP_TEMPLATE: _f_copy,
}


def format_observation(content: str, tool_name: str) -> str:
    data = _parse(content)
    if isinstance(data, dict) and data.get("error"):
        return _format_error(str(data["error"]))
    formatter = _FORMATTERS.get(tool_name)
    if formatter is not None:
        return formatter(data if isinstance(data, (dict, list)) else {})
    return "已完成该项操作"
