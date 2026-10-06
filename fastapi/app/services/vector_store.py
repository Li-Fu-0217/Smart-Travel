"""Chroma 向量库封装（见施工规范 §5 RAG、§9 阶段 5）。

嵌入模型 all-MiniLM-L6-v2（~79.3MB）不可用时视为可恢复状态：查询退化为关键词检索，
不报 500、不静默返回空。模型探测只做一次并缓存。
"""
import logging
import threading
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = settings.KNOWLEDGE_COLLECTION

_client = None
_collection = None
_model_ready: bool | None = None
_model_reason = ""
_detected = False
_lock = threading.Lock()


def _model_dir() -> Path:
    return Path.home() / ".cache" / "chroma" / "onnx_models" / "all-MiniLM-L6-v2"


def detect_model() -> tuple[bool, str]:
    """探测嵌入模型是否可用（只做一次并缓存）。"""
    global _model_ready, _model_reason, _detected
    with _lock:
        if _detected:
            return _model_ready, _model_reason
        _detected = True
        d = _model_dir()
        if not d.exists():
            _model_ready, _model_reason = False, f"嵌入模型未下载（{d} 不存在）"
        else:
            # 主判据：Chroma 把模型解压在 onnx/ 子目录（顶层只有 onnx/ 目录 + onnx.tar.gz）
            onnx_model = d / "onnx" / "model.onnx"
            onnx_config = d / "onnx" / "config.json"
            if onnx_model.exists() and onnx_config.exists():
                _model_ready, _model_reason = True, ""
            else:
                # 兼容顶层解压（部分版本把文件直接放在顶层）
                top_weights = any(f.name.endswith((".onnx", ".bin")) for f in d.iterdir() if f.is_file())
                top_config = (d / "config.json").exists()
                if top_weights and top_config:
                    _model_ready, _model_reason = True, ""
                else:
                    _model_ready, _model_reason = False, "嵌入模型不完整（onnx/model.onnx 不存在）"
        logger.info("嵌入模型可用=%s %s", _model_ready, _model_reason)
        return _model_ready, _model_reason


def _get_client():
    global _client
    if _client is None:
        import chromadb
        settings.chroma_root.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(settings.chroma_root))
    return _client


def get_collection():
    global _collection
    if _collection is None:
        _collection = _get_client().get_or_create_collection(
            name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )
    return _collection


def upsert_chunk(embedding_id: str, content: str, metadata: dict) -> bool:
    """写一条向量；模型不可用返回 False（不抛异常，不阻断切片落库）。"""
    ready, _ = detect_model()
    if not ready:
        return False
    try:
        get_collection().upsert(ids=[embedding_id], documents=[content], metadatas=[metadata])
        return True
    except Exception as e:
        logger.warning("向量写入失败 %s: %s", embedding_id, e)
        return False


def query_vectors(text: str, top_k: int) -> list[tuple[str, float]]:
    """向量检索，返回 [(embedding_id, score), ...]；模型不可用返回空列表。"""
    ready, _ = detect_model()
    if not ready:
        return []
    try:
        res = get_collection().query(query_texts=[text], n_results=top_k)
        ids = res.get("ids", [[]])[0]
        dists = res.get("distances", [[]])[0]
        return [(i, max(0.0, 1.0 - d)) for i, d in zip(ids, dists)]
    except Exception as e:
        logger.warning("向量检索失败: %s", e)
        return []


def delete_chunks(embedding_ids: list[str]) -> None:
    if not embedding_ids:
        return
    try:
        get_collection().delete(ids=embedding_ids)
    except Exception as e:
        logger.warning("向量删除失败: %s", e)


def count() -> int:
    try:
        return get_collection().count()
    except Exception:
        return 0
