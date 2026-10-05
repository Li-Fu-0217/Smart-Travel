"""业务表 SQLModel 映射（见施工规范 §9 阶段 3、§5.2、§5.6）。

映射全部 17 张业务表；唯一约束与索引只写在 sql/system.sql，此处不重复声明。
时间字段三档：
- 仅 create_time：`datetime = Field(default_factory=datetime.now)`
- 有 update_time：再加 `sa_column_kwargs={"onupdate": datetime.now}`
- 业务可空时间列（due_time / booking_time / visited_date 等）：`Optional[...] = None`，
  这些是 SQL 里 DEFAULT NULL 的合法可空列，不是 NOT NULL 的 create/update，不触发 1048。
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlmodel import Field, SQLModel


# =====================================================================
# 旅行者档案域
# =====================================================================

class TravelerProfile(SQLModel, table=True):
    __tablename__ = "traveler_profile"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    id_card_no: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    allergies: Optional[str] = None
    mobility_notes: Optional[str] = None
    preferences: Optional[str] = None
    preference_tags: Optional[str] = None
    preference_summary: Optional[str] = None
    preference_updated_at: Optional[datetime] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    status: int = 1
    create_time: datetime = Field(default_factory=datetime.now)
    update_time: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})


class FamilyMember(SQLModel, table=True):
    __tablename__ = "family_member"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    traveler_id: int
    relation: Optional[str] = None
    is_primary: int = 0
    create_time: datetime = Field(default_factory=datetime.now)


# =====================================================================
# 行程规划域
# =====================================================================

class TripPlan(SQLModel, table=True):
    __tablename__ = "trip_plan"

    id: Optional[int] = Field(default=None, primary_key=True)
    traveler_id: int
    title: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = None
    remark: Optional[str] = None
    status: int = 1
    source_template_id: Optional[int] = None
    create_time: datetime = Field(default_factory=datetime.now)
    update_time: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})


class TripTodo(SQLModel, table=True):
    __tablename__ = "trip_todo"

    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int
    traveler_id: int
    item_name: str
    due_time: Optional[datetime] = None
    category: str = "other"
    status: int = 2
    done_time: Optional[datetime] = None
    create_time: datetime = Field(default_factory=datetime.now)


# =====================================================================
# 行程模板域
# =====================================================================

class TripTemplate(SQLModel, table=True):
    __tablename__ = "trip_template"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    destination: Optional[str] = None
    day_count: int = 1
    description: Optional[str] = None
    author_user_id: Optional[int] = None
    author_name: Optional[str] = None
    cover: Optional[str] = None
    use_count: int = 0
    status: int = 1
    create_time: datetime = Field(default_factory=datetime.now)


class TripTemplateItem(SQLModel, table=True):
    __tablename__ = "trip_template_item"

    id: Optional[int] = Field(default=None, primary_key=True)
    template_id: int
    day_index: int = 1
    time_slot: Optional[str] = None
    item_name: str
    category: str = "other"
    remark: Optional[str] = None
    sort_order: int = 0


# =====================================================================
# 预约域
# =====================================================================

class BookingCatalog(SQLModel, table=True):
    __tablename__ = "booking_catalog"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    item_type: str
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    price: Optional[Decimal] = None
    status: int = 1
    create_time: datetime = Field(default_factory=datetime.now)


class BookingOrder(SQLModel, table=True):
    __tablename__ = "booking_order"

    id: Optional[int] = Field(default=None, primary_key=True)
    traveler_id: int
    catalog_id: int
    booking_time: Optional[datetime] = None
    guest_count: int = 1
    status: str = "pending"
    source: str = "manual"
    slot_lock: Optional[str] = None
    version: int = 0
    remark: Optional[str] = None
    create_time: datetime = Field(default_factory=datetime.now)
    update_time: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})


# =====================================================================
# 拼团活动域
# =====================================================================

class GroupTour(SQLModel, table=True):
    __tablename__ = "group_tour"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: Optional[str] = None
    destination: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    capacity: int = 0
    status: int = 1
    create_time: datetime = Field(default_factory=datetime.now)


class GroupTourSignup(SQLModel, table=True):
    __tablename__ = "group_tour_signup"

    id: Optional[int] = Field(default=None, primary_key=True)
    tour_id: int
    traveler_id: int
    user_id: int
    status: str = "registered"
    create_time: datetime = Field(default_factory=datetime.now)


# =====================================================================
# 旅途求助域
# =====================================================================

class TravelAlert(SQLModel, table=True):
    __tablename__ = "travel_alert"

    id: Optional[int] = Field(default=None, primary_key=True)
    traveler_id: int
    location: Optional[str] = None
    message: Optional[str] = None
    alert_type: str = "other"
    status: str = "open"
    notify_family: int = 0
    notify_staff: int = 0
    source: str = "manual"
    create_time: datetime = Field(default_factory=datetime.now)


# =====================================================================
# 旅游记录域
# =====================================================================

class TravelRecord(SQLModel, table=True):
    __tablename__ = "travel_record"

    id: Optional[int] = Field(default=None, primary_key=True)
    traveler_id: int
    trip_id: Optional[int] = None
    destination: Optional[str] = None
    visited_date: Optional[date] = None
    rating: Optional[int] = None
    content: Optional[str] = None
    photos: Optional[str] = None
    visibility: int = 0
    create_time: datetime = Field(default_factory=datetime.now)


# =====================================================================
# 攻略知识库域（RAG，阶段 5 实现 service）
# =====================================================================

class GuideDocument(SQLModel, table=True):
    __tablename__ = "guide_document"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    file_path: str
    doc_type: str
    destination: Optional[str] = None
    status: int = 0
    create_time: datetime = Field(default_factory=datetime.now)


class GuideChunk(SQLModel, table=True):
    __tablename__ = "guide_chunk"

    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int
    chunk_index: int = 0
    content: Optional[str] = None
    embedding_id: Optional[str] = None


# =====================================================================
# 通知域
# =====================================================================

class NotifyInbox(SQLModel, table=True):
    __tablename__ = "notify_inbox"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    traveler_id: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    msg_type: str = "system"
    source: str = "system"
    related_id: Optional[int] = None
    is_read: int = 0
    create_time: datetime = Field(default_factory=datetime.now)


# =====================================================================
# 智能助手域（阶段 6 实现 service）
# =====================================================================

class AgentConversation(SQLModel, table=True):
    __tablename__ = "agent_conversation"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    traveler_id: Optional[int] = None
    session_id: str
    role: str
    content: Optional[str] = None
    create_time: datetime = Field(default_factory=datetime.now)


class AgentToolCallLog(SQLModel, table=True):
    __tablename__ = "agent_tool_call_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: Optional[str] = None
    user_id: Optional[int] = None
    tool_name: str
    request_args: Optional[str] = None
    response_data: Optional[str] = None
    status: int = 1
    cost_ms: Optional[int] = None
    create_time: datetime = Field(default_factory=datetime.now)
