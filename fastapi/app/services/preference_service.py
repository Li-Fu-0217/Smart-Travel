"""偏好提炼服务（见施工规范 §4.5、§5.8）。"""
from datetime import datetime
from typing import List

from sqlmodel import Session, select

from app.common.constants import PREFERENCE_KEYWORDS, PREFERENCE_TAGS
from app.common.exceptions import BusinessException
from app.models import SysUser, TravelRecord, TravelerProfile
from app.services.family_service import assert_family_access
from app.services.traveler_service import to_profile_vo


def _get_traveler(db: Session, user: SysUser, traveler_id: int) -> TravelerProfile:
    assert_family_access(db, user, traveler_id)
    traveler = db.get(TravelerProfile, traveler_id)
    if traveler is None:
        raise BusinessException("旅行者不存在", code=404)
    return traveler


def distill(db: Session, user: SysUser, traveler_id: int):
    """从旅游记录提炼偏好标签：关键词命中 PREFERENCE_KEYWORDS，再用 PREFERENCE_TAGS 过滤。"""
    traveler = _get_traveler(db, user, traveler_id)
    records = db.exec(select(TravelRecord).where(TravelRecord.traveler_id == traveler_id)).all()
    text = " ".join(
        f"{r.content or ''} {r.destination or ''}" for r in records
    )
    tags: List[str] = []
    for tag, keywords in PREFERENCE_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            tags.append(tag)
    tags = [t for t in tags if t in PREFERENCE_TAGS]  # 双重保险，杜绝自创标签
    traveler.preference_tags = ",".join(tags) if tags else None
    traveler.preference_summary = "、".join(tags) if tags else None
    traveler.preference_updated_at = datetime.now()
    db.add(traveler)
    db.commit()
    db.refresh(traveler)
    return to_profile_vo(traveler)


def update_preferences(db: Session, user: SysUser, traveler_id: int, tags: List[str]):
    traveler = _get_traveler(db, user, traveler_id)
    for tag in tags:
        if tag not in PREFERENCE_TAGS:
            raise BusinessException("偏好标签不合法", code=400)
    traveler.preference_tags = ",".join(tags) if tags else None
    traveler.preference_summary = "、".join(tags) if tags else None
    traveler.preference_updated_at = datetime.now()
    db.add(traveler)
    db.commit()
    db.refresh(traveler)
    return to_profile_vo(traveler)
