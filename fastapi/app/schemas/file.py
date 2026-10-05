"""文件出入参（见施工规范 §4.8）。"""
from app.common.result import CamelModel


class FileVO(CamelModel):
    path: str
    name: str
    size: int
    category: str
