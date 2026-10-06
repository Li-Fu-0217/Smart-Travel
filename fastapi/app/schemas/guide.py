"""攻略库出入参（见施工规范 §4.5、§5.8、§5 RAG）。"""
from typing import List

from app.common.result import CamelModel, DateTimeStr


class GuideDocumentVO(CamelModel):
    id: int
    title: str
    file_path: str
    doc_type: str
    destination: str | None = None
    status: int = 0
    create_time: DateTimeStr | None = None


class GuideChunkVO(CamelModel):
    id: int
    document_id: int
    chunk_index: int
    content: str | None = None
    embedding_id: str | None = None


class GuideQueryHitVO(CamelModel):
    document_id: int
    title: str | None = None
    content: str
    score: float


class GuideQueryResponseVO(CamelModel):
    results: List[GuideQueryHitVO] = []
    degraded: bool = False
    message: str = ""
