"""看板统计服务（见施工规范 §7.7）。

硬性要求：不用 COUNT(*) 全表扫再在 Python 里过滤，直接在 SQL 层用 func.count() + where 聚合；
近 7 日折线图的补零逻辑在后端显式写（不依赖前端补）。
"""
from datetime import date, timedelta
from typing import List

from sqlmodel import Session, func, select

from app.agent.tool_catalog import CATALOG
from app.common.constants import BOOKING_STATUS, ITEM_TYPES
from app.models import (
    AgentToolCallLog,
    BookingCatalog,
    BookingOrder,
    FamilyMember,
    GroupTour,
    GuideDocument,
    NotifyInbox,
    SysUser,
    TravelAlert,
    TravelerProfile,
    TripTodo,
)

# 预约状态 → 中文（§7.7 饼图标签）
_BOOKING_STATUS_CN = {"pending": "待确认", "confirmed": "已确认", "cancelled": "已取消", "done": "已完成"}
# 项目类型 → 中文
_ITEM_TYPE_CN = {"guide": "导游", "homestay": "民宿", "experience": "体验", "ticket": "门票"}
# 工具名 → 中文（取自 tool_catalog.py，与助手工具说明书一致）
_TOOL_LABEL = {c["name"]: c["label"] for c in CATALOG}


def _count(db: Session, model, *conds) -> int:
    stmt = select(func.count(model.id))
    for c in conds:
        stmt = stmt.where(c)
    return db.exec(stmt).one()


def _booking_status(db: Session) -> list[dict]:
    rows = db.exec(select(BookingOrder.status, func.count(BookingOrder.id)).group_by(BookingOrder.status)).all()
    counts = {s: n for s, n in rows}
    return [{"name": _BOOKING_STATUS_CN.get(s, s), "value": counts.get(s, 0)} for s in BOOKING_STATUS]


def _item_type_count(db: Session) -> list[dict]:
    rows = db.exec(
        select(BookingCatalog.item_type, func.count(BookingOrder.id))
        .join(BookingCatalog, BookingOrder.catalog_id == BookingCatalog.id)
        .group_by(BookingCatalog.item_type)
    ).all()
    counts = {t: n for t, n in rows}
    return [{"name": _ITEM_TYPE_CN.get(t, t), "value": counts.get(t, 0)} for t in ITEM_TYPES]


def _trend_7d(db: Session) -> list[dict]:
    """近 7 日预约趋势：按 DATE(create_time) 分组，缺失日期补 0（后端显式补零）。"""
    today = date.today()
    start = today - timedelta(days=6)
    rows = db.exec(
        select(func.date(BookingOrder.create_time), func.count(BookingOrder.id))
        .where(func.date(BookingOrder.create_time) >= start)
        .group_by(func.date(BookingOrder.create_time))
    ).all()
    counts = {str(d): n for d, n in rows}
    result = []
    for i in range(7):
        d = start + timedelta(days=i)
        result.append({"date": d.isoformat(), "count": counts.get(d.isoformat(), 0)})
    return result


def _tool_distribution(db: Session) -> list[dict]:
    rows = db.exec(select(AgentToolCallLog.tool_name, func.count(AgentToolCallLog.id)).group_by(AgentToolCallLog.tool_name)).all()
    return [{"name": _TOOL_LABEL.get(n, n), "value": c} for n, c in rows]


def admin_stats(db: Session) -> dict:
    """管理端 8 KPI + 4 图表（§7.7）。"""
    kpis = {
        "travelers": _count(db, TravelerProfile, TravelerProfile.status == 1),
        "activeUsers": _count(db, SysUser, SysUser.role == "USER", SysUser.status == 1),
        "pendingBookings": _count(db, BookingOrder, BookingOrder.status == "pending"),
        "openAlerts": _count(db, TravelAlert, TravelAlert.status.in_(("open", "handling"))),
        "activeTours": _count(db, GroupTour, GroupTour.status == 1),
        "overdueTodos": _count(db, TripTodo, TripTodo.status == 2, TripTodo.due_time < func.now()),
        "guideDocs": _count(db, GuideDocument),
        "guideReady": _count(db, GuideDocument, GuideDocument.status == 1),
        "agentCalls": _count(db, AgentToolCallLog),
    }
    charts = {
        "bookingStatus": _booking_status(db),
        "itemTypeCount": _item_type_count(db),
        "trend7d": _trend_7d(db),
        "toolDistribution": _tool_distribution(db),
    }
    return {"kpis": kpis, "charts": charts}


def front_dashboard(db: Session, user: SysUser) -> dict:
    """用户前台关怀看板摘要（§7.7）：已绑定旅行者 + 未读消息 + 逾期待办。"""
    traveler_ids = db.exec(select(FamilyMember.traveler_id).where(FamilyMember.user_id == user.id)).all()
    unread = _count(db, NotifyInbox, NotifyInbox.user_id == user.id, NotifyInbox.is_read == 0)
    overdue = 0
    if traveler_ids:
        overdue = _count(
            db, TripTodo,
            TripTodo.traveler_id.in_(traveler_ids),
            TripTodo.status == 2,
            TripTodo.due_time < func.now(),
        )
    return {"travelerCount": len(traveler_ids), "unreadCount": unread, "overdueCount": overdue}
