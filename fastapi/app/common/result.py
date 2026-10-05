"""统一响应与字段命名（见施工规范 §4.2）。"""
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class CamelModel(BaseModel):
    """出参基类：Python snake_case 自动转前端 camelCase。"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class Result(CamelModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


class PageResult(CamelModel, Generic[T]):
    records: List[T] = []
    total: int = 0
    current: int = 1
    size: int = 10
