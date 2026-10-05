"""全局枚举与词表常量（见施工规范 §5.8）。

把 §5.8 的全部固定取值集中在此单一权威来源，
schema 校验、distill 关键词映射、前端下拉/标签映射均引用这里，禁止各处写裸字符串。
"""

# 偏好标签（固定 9 个，逗号分隔存于 traveler_profile.preference_tags）
PREFERENCE_TAGS: frozenset[str] = frozenset({
    "海岛", "人文", "自然", "美食", "亲子", "摄影", "购物", "探险", "休闲",
})

# 偏好提炼「关键词 → 标签」映射（阶段 3.4 distill 使用）。
# 与 PREFERENCE_TAGS 是同一份权威数据的两个视角：key 全部落在 9 词表内，
# distill 命中关键词后仍会再用 PREFERENCE_TAGS 过滤，杜绝自创标签。
PREFERENCE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "海岛": ("海岛", "海景", "海滩", "海边", "岛屿"),
    "人文": ("人文", "古城", "古镇", "博物馆", "历史", "古迹", "建筑", "寺庙", "文化", "遗址", "水乡", "石窟"),
    "自然": ("自然", "山水", "森林", "湖泊", "峡谷", "风景", "雪山", "草原"),
    "美食": ("美食", "海鲜", "小吃", "夜市", "早市", "特色菜", "啤酒"),
    "亲子": ("亲子", "孩子", "带娃", "小孩", "儿童", "乐园", "家庭"),
    "摄影": ("摄影", "出片", "拍照", "取景"),
    "购物": ("购物", "逛街", "市场", "特产", "小店"),
    "探险": ("探险", "徒步", "小众", "户外", "攀岩", "漂流", "越野"),
    "休闲": ("休闲", "度假", "发呆", "放松", "慢", "节奏", "骑行", "温泉"),
}

# 可预约项目类型（booking_catalog.item_type、前端下拉、工具参数）
ITEM_TYPES: frozenset[str] = frozenset({"guide", "homestay", "experience", "ticket"})

# 待办 / 模板明细分类（trip_todo.category 与 trip_template_item.category 共用同一词表）
TODO_CATEGORIES: frozenset[str] = frozenset({"visa", "insurance", "vaccine", "luggage", "transfer", "other"})

# 模板日程时段（trip_template_item.time_slot）
TIME_SLOTS: frozenset[str] = frozenset({"09:00", "14:00", "19:00", "全天"})

# 攻略文档分类（guide_document.doc_type）
DOC_TYPES: frozenset[str] = frozenset({"visa", "document", "destination", "tips"})

# 站内消息类型（notify_inbox.msg_type）
MSG_TYPES: frozenset[str] = frozenset({"agent_notify", "trip_reminder", "booking", "alert", "system"})

# 旅途求助类型（travel_alert.alert_type）
ALERT_TYPES: frozenset[str] = frozenset({"lost", "illness", "document", "accident", "other"})

# 预约订单状态（booking_order.status）
BOOKING_STATUS: frozenset[str] = frozenset({"pending", "confirmed", "cancelled", "done"})

# 拼团报名状态（group_tour_signup.status）
SIGNUP_STATUS: frozenset[str] = frozenset({"registered", "cancelled"})

# 求助工单状态（travel_alert.status）
ALERT_STATUS: frozenset[str] = frozenset({"open", "handling", "closed"})

# 操作来源（booking_order.source / travel_alert.source / notify_inbox.source）
SOURCES: frozenset[str] = frozenset({"manual", "agent", "system"})
