"""行程推荐服务（见施工规范 §6.2 工具 8、§6.12）。

只读：根据旅行者偏好标签 + 历史旅游记录，生成一份行程方案。返回结构对齐 §6.12 ItineraryCard
（title / destination / day_count / days[{day_index,title,items}] / tags / tips），
作为行程卡片结构化抽取的素材。禁止越权读取他人记录（经 assert_family_access 闸门）。
"""
from sqlmodel import Session, select

from app.common.constants import PREFERENCE_KEYWORDS, PREFERENCE_TAGS
from app.common.exceptions import BusinessException
from app.models import SysUser, TravelRecord, TravelerProfile
from app.services.family_service import assert_family_access

# 标签 → 建议活动条目（无 LLM 时生成演示级推荐内容的静态素材）
_TAG_ACTIVITIES: dict[str, list[str]] = {
    "海岛": ["海边漫步看日出", "海岛浮潜/沙滩休闲", "海鲜市场寻味"],
    "人文": ["古城/古镇深度游", "博物馆与历史街区", "地道小吃探店"],
    "自然": ["山水景区徒步", "湖泊/森林观景", "自然风光摄影"],
    "美食": ["本地早市/夜市", "特色菜馆打卡", "美食街区逛吃"],
    "亲子": ["主题乐园/亲子场馆", "亲子手作体验", "儿童友好公园"],
    "摄影": ["日出/日落取景点", "网红出片机位", "人文街拍"],
    "购物": ["本地特产采购", "特色市集/商圈", "伴手礼挑选"],
    "探险": ["小众徒步路线", "户外体验项目", "秘境探访"],
    "休闲": ["温泉/SPA 放松", "咖啡馆/茶馆发呆", "慢节奏街区散步"],
}

_DAY_TITLES = ("抵达与初体验", "核心体验日", "深度探索", "慢游与返程")


def _derive_tags(profile: TravelerProfile, records_text: str) -> list[str]:
    tags: list[str] = []
    if profile.preference_tags:
        tags = [t for t in profile.preference_tags.split(",") if t in PREFERENCE_TAGS]
    if not tags:  # 档案无偏好时，从历史记录关键词反推
        for tag, kws in PREFERENCE_KEYWORDS.items():
            if any(kw in records_text for kw in kws):
                tags.append(tag)
    return (tags or ["休闲"])[:4]


def recommend(db: Session, user: SysUser, traveler_id: int) -> dict:
    assert_family_access(db, user, traveler_id)
    traveler = db.get(TravelerProfile, traveler_id)
    if traveler is None:
        raise BusinessException("旅行者不存在", code=404)
    records = db.exec(
        select(TravelRecord)
        .where(TravelRecord.traveler_id == traveler_id)
        .order_by(TravelRecord.id.desc())
    ).all()
    records_text = " ".join(f"{r.destination or ''} {r.content or ''}" for r in records)

    tags = _derive_tags(traveler, records_text)
    destination = (records[0].destination if records else None) or "热门目的地"
    day_count = min(max(len(tags) + 1, 3), 5)

    days = []
    for i in range(day_count):
        tag = tags[i % len(tags)]
        acts = _TAG_ACTIVITIES.get(tag, _TAG_ACTIVITIES["休闲"])
        days.append({
            "day_index": i + 1,
            "title": _DAY_TITLES[min(i, len(_DAY_TITLES) - 1)],
            "items": [acts[i % len(acts)], acts[(i + 1) % len(acts)]],
        })

    return {
        "title": f"{destination} {'·'.join(tags[:2])} {day_count} 日游",
        "destination": destination,
        "day_count": day_count,
        "days": days,
        "tags": tags,
        "tips": "根据您的偏好标签与历史旅游记录生成，可复制行程模板或直接预约当地体验",
    }
