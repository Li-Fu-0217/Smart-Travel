"""攻略库服务（见施工规范 §5 RAG、§9 阶段 5）。"""
import re
from pathlib import Path
from typing import List, Optional

from sqlmodel import Session, func, select

from app.common.exceptions import BusinessException
from app.core.config import settings
from app.models import GuideChunk, GuideDocument
from app.schemas.guide import (
    GuideChunkVO,
    GuideDocumentVO,
    GuideQueryHitVO,
    GuideQueryResponseVO,
)
from app.services import vector_store

CHUNK_SIZE = 280
CHUNK_OVERLAP = 40
TOP_K = 5


# ===== 切片（段优先，块长约 280、重叠约 40）=====

def _split_text(text: str) -> List[str]:
    text = text.strip()
    if not text:
        return []
    sentences = re.split(r'(?<=[。！？!?\n])', text)
    chunks: List[str] = []
    buf = ""
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if len(buf) + len(s) <= CHUNK_SIZE:
            buf += s
        else:
            if buf:
                chunks.append(buf)
            while len(s) > CHUNK_SIZE:
                chunks.append(s[:CHUNK_SIZE])
                s = s[CHUNK_SIZE - CHUNK_OVERLAP:]
            buf = s
    if buf:
        chunks.append(buf)
    return chunks


# ===== 关键词 n-gram（权重 1.2）=====

def _keyword_score(query: str, content: str) -> float:
    score = 0.0
    for n in (2, 3, 4):
        for i in range(len(query) - n + 1):
            if query[i:i + n] in content:
                score += 1.0
    return score * 1.2


# ===== 文件解析 =====

def parse_file(file_path: str) -> str:
    """把 /uploads/... 或 seed/... 路径解析为文本。"""
    if file_path.startswith("/uploads/"):
        full = settings.upload_root / file_path[len("/uploads/"):]
    elif file_path.startswith("seed/"):
        full = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_seed" / file_path[len("seed/"):]
    else:
        full = settings.upload_root / file_path
    if not full.exists():
        raise BusinessException("文件不存在", code=404)
    suffix = full.suffix.lower()
    if suffix in (".txt", ".md"):
        return full.read_text(encoding="utf-8")
    if suffix == ".pdf":
        from pypdf import PdfReader
        return "\n".join((p.extract_text() or "") for p in PdfReader(str(full)).pages)
    raise BusinessException("不支持的文件类型", code=400)


# ===== VO =====

def to_doc_vo(d: GuideDocument) -> GuideDocumentVO:
    return GuideDocumentVO(
        id=d.id, title=d.title, file_path=d.file_path, doc_type=d.doc_type,
        destination=d.destination, status=d.status, create_time=d.create_time,
    )


def to_chunk_vo(c: GuideChunk) -> GuideChunkVO:
    return GuideChunkVO(
        id=c.id, document_id=c.document_id, chunk_index=c.chunk_index,
        content=c.content, embedding_id=c.embedding_id,
    )


# ===== 文档管理 =====

def list_documents(db: Session, current: int, size: int, keyword: str) -> tuple[List[GuideDocumentVO], int]:
    stmt = select(GuideDocument)
    count_stmt = select(func.count(GuideDocument.id))
    if keyword:
        cond = GuideDocument.title.contains(keyword)
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)
    total = db.exec(count_stmt).one()
    docs = db.exec(stmt.order_by(GuideDocument.id).offset((current - 1) * size).limit(size)).all()
    return [to_doc_vo(d) for d in docs], total


def get_chunks(db: Session, document_id: int) -> List[GuideChunkVO]:
    if db.get(GuideDocument, document_id) is None:
        raise BusinessException("攻略文档不存在", code=404)
    chunks = db.exec(
        select(GuideChunk).where(GuideChunk.document_id == document_id).order_by(GuideChunk.chunk_index)
    ).all()
    return [to_chunk_vo(c) for c in chunks]


def _vectorize_document(db: Session, document_id: int) -> bool:
    chunks = db.exec(select(GuideChunk).where(GuideChunk.document_id == document_id)).all()
    if not chunks:
        return True
    ok_all = True
    for c in chunks:
        eid = f"chunk-{c.id}"
        if vector_store.upsert_chunk(eid, c.content or "", {"document_id": document_id, "chunk_index": c.chunk_index}):
            c.embedding_id = eid
            db.add(c)
        else:
            ok_all = False
    db.commit()
    return ok_all


def create_document(db: Session, title: str, file_path: str, doc_type: str, destination: Optional[str], text: str) -> GuideDocumentVO:
    if not text or not text.strip():
        raise BusinessException("文档内容为空，无法切片", code=400)
    doc = GuideDocument(title=title, file_path=file_path, doc_type=doc_type, destination=destination, status=0)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    chunks = _split_text(text)
    for i, c in enumerate(chunks):
        db.add(GuideChunk(document_id=doc.id, chunk_index=i, content=c))
    db.commit()
    if _vectorize_document(db, doc.id):
        doc.status = 1
        db.add(doc)
        db.commit()
        db.refresh(doc)
    return to_doc_vo(doc)


def delete_document(db: Session, document_id: int) -> None:
    doc = db.get(GuideDocument, document_id)
    if doc is None:
        raise BusinessException("攻略文档不存在", code=404)
    chunks = db.exec(select(GuideChunk).where(GuideChunk.document_id == document_id)).all()
    eids = [c.embedding_id for c in chunks if c.embedding_id]
    for c in chunks:
        db.delete(c)
    db.delete(doc)
    db.commit()
    vector_store.delete_chunks(eids)
    # seed/ 前缀跳过删原文件（§5.5）


# ===== 检索 =====

def query(db: Session, text: str) -> GuideQueryResponseVO:
    if not text or not text.strip():
        raise BusinessException("检索词不能为空", code=400)
    chunks = db.exec(select(GuideChunk)).all()
    doc_titles = {d.id: d.title for d in db.exec(select(GuideDocument)).all()}

    kw = {c.id: _keyword_score(text, c.content or "") for c in chunks}

    ready, reason = vector_store.detect_model()
    vec = {}
    if ready:
        for eid, score in vector_store.query_vectors(text, TOP_K * 2):
            try:
                vec[int(eid.replace("chunk-", ""))] = score
            except ValueError:
                continue

    merged = []
    for c in chunks:
        total = 0.6 * vec.get(c.id, 0.0) + 1.2 * kw.get(c.id, 0.0)
        if total > 0:
            merged.append((c, total))
    merged.sort(key=lambda x: -x[1])
    hits = [
        GuideQueryHitVO(document_id=c.document_id, title=doc_titles.get(c.document_id), content=c.content or "", score=round(s, 4))
        for c, s in merged[:TOP_K]
    ]

    degraded = not ready
    message = "嵌入模型不可用，已退化为关键词检索" if degraded else ""
    if not hits:
        message = "攻略库暂未检索到很贴切的内容，换个问法或咨询客服"
    return GuideQueryResponseVO(results=hits, degraded=degraded, message=message)


# ===== 种子向量化 =====

def seed_vectors(db: Session) -> dict:
    ready, reason = vector_store.detect_model()
    doc_ids = db.exec(select(GuideDocument.id)).all()
    n_vec = 0
    for did in doc_ids:
        if _vectorize_document(db, did):
            db.get(GuideDocument, did).status = 1
            n_vec += 1
    db.commit()
    return {"model_ready": ready, "reason": reason, "vectorized_docs": n_vec, "total_docs": len(doc_ids)}
