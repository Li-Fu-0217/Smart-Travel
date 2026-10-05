"""行程模板出入参（见施工规范 §4.5、§5.2、§5.8）。"""
from datetime import date
from typing import List

from pydantic import Field

from app.common.result import CamelModel, DateTimeStr


class TemplatePublishRequest(CamelModel):
    trip_id: int
    title: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=500)


class TemplateCopyRequest(CamelModel):
    traveler_id: int
    start_date: date


class TemplateUpdateRequest(CamelModel):
    title: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=500)
    status: int | None = None


class TemplateItemVO(CamelModel):
    id: int
    template_id: int
    day_index: int
    time_slot: str | None = None
    item_name: str
    category: str = "other"
    remark: str | None = None
    sort_order: int = 0


class TemplateVO(CamelModel):
    id: int
    title: str
    destination: str | None = None
    day_count: int = 1
    description: str | None = None
    author_user_id: int | None = None
    author_name: str | None = None
    cover: str | None = None
    use_count: int = 0
    status: int = 1
    create_time: DateTimeStr | None = None


class TemplateDetailVO(TemplateVO):
    items: List[TemplateItemVO] = []
