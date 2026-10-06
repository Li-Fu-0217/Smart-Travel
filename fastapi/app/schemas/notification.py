"""站内消息出入参（见施工规范 §4.5、§5.8）。"""
from app.common.result import CamelModel, DateTimeStr


class NotificationVO(CamelModel):
    id: int
    user_id: int
    traveler_id: int | None = None
    title: str | None = None
    content: str | None = None
    msg_type: str = "system"
    source: str = "system"
    related_id: int | None = None
    is_read: int = 0
    create_time: DateTimeStr | None = None
