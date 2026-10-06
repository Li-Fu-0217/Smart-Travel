"""工具说明书（见施工规范 §6.10）。

供管理端「助手工具」页面展示：工具名、中文名、分类、有无副作用、作用、参数、使用规则、示例问法。
内容必须与 tools.py 逐字对齐（工具名、参数名）——工具名直接引用 tools.TOOL_* 常量，参数名用
ARGS_SCHEMAS 校验，从机制上杜绝两处漂移。
"""
from app.agent import tools

CATALOG: list[dict] = [
    {
        "name": tools.TOOL_QUERY_TRAVELER_PROFILE,
        "label": "查询旅行者档案",
        "category": "档案",
        "side_effect": False,
        "description": "查询旅行者档案：出行偏好、忌口、过敏、行动不便说明，附带近期逾期待办概况",
        "params": [{"name": "traveler_id", "type": "int", "required": True, "desc": "旅行者ID"}],
        "rules": "仅可查询已绑定旅行者；须过归属校验",
        "examples": ["我家人的饮食有什么忌口？", "看看陈小雨的出行偏好"],
    },
    {
        "name": tools.TOOL_CHECK_TRIP_SCHEDULE,
        "label": "查询行程待办",
        "category": "行程",
        "side_effect": False,
        "description": "查询行程待办（签证/保险/接送机等）及逾期情况",
        "params": [{"name": "traveler_id", "type": "int", "required": True, "desc": "旅行者ID"}],
        "rules": "仅可查询已绑定旅行者；不改写完成状态",
        "examples": ["看看我家人这周的行程待办", "有哪些待办快逾期了？"],
    },
    {
        "name": tools.TOOL_QUERY_AVAILABLE_BOOKING,
        "label": "查询可预约时段",
        "category": "预约",
        "side_effect": False,
        "description": "按项目类型查询可预约项目与未来可用时段",
        "params": [
            {"name": "item_type", "type": "str", "required": False, "desc": "预约项目类型：guide/homestay/experience/ticket"},
            {"name": "days", "type": "int", "required": False, "desc": "查询未来几天（默认 3）"},
        ],
        "rules": "登录用户；想预约前必须先查这里",
        "examples": ["这周有什么当地体验可以约？", "帮我看看门票可约时段"],
    },
    {
        "name": tools.TOOL_BOOK_ITEM,
        "label": "提交预约订单",
        "category": "预约",
        "side_effect": True,
        "description": "为旅行者提交预约订单（source=agent）",
        "params": [
            {"name": "traveler_id", "type": "int", "required": True, "desc": "旅行者ID"},
            {"name": "catalog_id", "type": "int", "required": True, "desc": "预约项目ID"},
            {"name": "slot", "type": "str", "required": True, "desc": "预约时段，如 2026-03-12 09:00"},
            {"name": "guest_count", "type": "int", "required": False, "desc": "人数"},
            {"name": "remark", "type": "str", "required": False, "desc": "备注"},
        ],
        "rules": "须已绑定；防超卖；须用户明确确认后才能调用",
        "examples": ["就约这个时段", "帮我订第一个时段"],
    },
    {
        "name": tools.TOOL_NOTIFY_COMPANIONS,
        "label": "通知同行人",
        "category": "通知",
        "side_effect": True,
        "description": "向该旅行者的绑定联系人发送站内消息",
        "params": [
            {"name": "traveler_id", "type": "int", "required": True, "desc": "旅行者ID"},
            {"name": "message", "type": "str", "required": True, "desc": "要通知的内容"},
        ],
        "rules": "无绑定时通知数为 0",
        "examples": ["预约成功提醒一下家人", "把逾期情况告诉同行人"],
    },
    {
        "name": tools.TOOL_TRIGGER_TRAVEL_ALERT,
        "label": "旅途求助",
        "category": "求助",
        "side_effect": True,
        "description": "创建旅途求助工单并通知紧急联系人",
        "params": [
            {"name": "traveler_id", "type": "int", "required": True, "desc": "旅行者ID"},
            {"name": "location", "type": "str", "required": False, "desc": "当前位置"},
            {"name": "message", "type": "str", "required": False, "desc": "求助说明"},
            {"name": "alert_type", "type": "str", "required": False, "desc": "求助类型：lost/illness/document/accident/other"},
        ],
        "rules": "须已绑定；无绑定也保留工单",
        "examples": ["我在景区和队伍走散了", "身体不适需要求助"],
    },
    {
        "name": tools.TOOL_QUERY_GUIDE_KNOWLEDGE,
        "label": "攻略检索",
        "category": "攻略",
        "side_effect": False,
        "description": "RAG 检索攻略库（签证政策、目的地指南、出行注意事项）",
        "params": [{"name": "query", "type": "str", "required": True, "desc": "检索关键词或问题"}],
        "rules": "登录用户；检索不到时如实告知，不得编造政策",
        "examples": ["申根签证要什么材料？", "带小孩出行要注意什么？"],
    },
    {
        "name": tools.TOOL_RECOMMEND_ITINERARY,
        "label": "行程推荐",
        "category": "推荐",
        "side_effect": False,
        "description": "根据旅行者偏好与历史旅游记录，推荐行程方案",
        "params": [{"name": "traveler_id", "type": "int", "required": True, "desc": "旅行者ID"}],
        "rules": "须已绑定；禁止越权读取他人记录",
        "examples": ["根据我以前的旅行记录推荐下次去哪", "帮我规划一个海岛行程"],
    },
    {
        "name": tools.TOOL_SAVE_TRAVEL_RECORD,
        "label": "写入旅游记录",
        "category": "记录",
        "side_effect": True,
        "description": "为旅行者写入一条旅游记录（目的地、评分、感受）",
        "params": [
            {"name": "traveler_id", "type": "int", "required": True, "desc": "旅行者ID"},
            {"name": "destination", "type": "str", "required": True, "desc": "目的地"},
            {"name": "rating", "type": "int", "required": False, "desc": "评分 1-5"},
            {"name": "content", "type": "str", "required": False, "desc": "感受/评价"},
        ],
        "rules": "须已绑定",
        "examples": ["记录一下我上个月去了三亚，五颗星", "帮我记一条旅游记录"],
    },
    {
        "name": tools.TOOL_DISTILL_PREFERENCES,
        "label": "偏好提炼",
        "category": "偏好",
        "side_effect": True,
        "description": "从该旅行者的历史旅游记录中提炼偏好，回写到档案的偏好标签与摘要",
        "params": [{"name": "traveler_id", "type": "int", "required": True, "desc": "旅行者ID"}],
        "rules": "须已绑定；只读自己的记录",
        "examples": ["总结一下我的旅行喜好", "根据我的记录更新偏好"],
    },
    {
        "name": tools.TOOL_COPY_TRIP_TEMPLATE,
        "label": "复制行程模板",
        "category": "模板",
        "side_effect": True,
        "description": "把某个行程模板复制成该旅行者的一份新行程（含日程明细）",
        "params": [
            {"name": "traveler_id", "type": "int", "required": True, "desc": "旅行者ID"},
            {"name": "template_id", "type": "int", "required": True, "desc": "行程模板ID"},
            {"name": "start_date", "type": "str", "required": True, "desc": "行程开始日期 YYYY-MM-DD"},
        ],
        "rules": "须已绑定；模板须为已发布状态",
        "examples": ["就按这个模板复制成行程", "把大理 4 日游套用成我的行程"],
    },
]


def _validate_alignment() -> None:
    """工具说明书与 tools.py 逐字对齐的运行时断言（§6.10）。"""
    names = [c["name"] for c in CATALOG]
    assert names == list(tools.TOOL_NAMES), f"工具说明书与 tools.py 工具名不一致：{names} vs {list(tools.TOOL_NAMES)}"
    for c in CATALOG:
        schema = tools.ARGS_SCHEMAS[c["name"]]
        catalog_params = {p["name"] for p in c["params"]}
        schema_params = set(schema.model_fields.keys())
        assert catalog_params == schema_params, f"{c['name']} 参数不一致：{catalog_params} vs {schema_params}"


_validate_alignment()
