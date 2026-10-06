"""攻略库接口（见施工规范 §4.5、§5 RAG）。"""
from fastapi import APIRouter, Depends, Query, Request
from pydantic import Field, field_validator
from sqlmodel import Session

from app.common.constants import DOC_TYPES
from app.common.result import CamelModel, PageResult, Result
from app.core.deps import get_current_user, get_db, operation_log, require_admin
from app.services import guide_service

router = APIRouter(prefix="/guides", tags=["攻略库"])
admin_router = APIRouter(prefix="/admin/guides", tags=["攻略库"])


class GuideQueryRequest(CamelModel):
    text: str = Field(..., min_length=1, max_length=200)


class GuideDocumentCreateRequest(CamelModel):
    title: str = Field(..., min_length=1, max_length=200)
    file_path: str = Field(..., min_length=1, max_length=255)
    doc_type: str = Field(..., min_length=1, max_length=20)
    destination: str | None = None

    @field_validator("doc_type")
    @classmethod
    def _check_doc_type(cls, v: str) -> str:
        if v not in DOC_TYPES:
            raise ValueError("攻略文档类型不合法")
        return v


@router.post("/query")
def query(payload: GuideQueryRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=guide_service.query(db, payload.text))


@admin_router.get("/documents")
def list_documents(
    current: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: str = Query(""),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    records, total = guide_service.list_documents(db, current, size, keyword)
    return Result(data=PageResult(records=records, total=total, current=current, size=size))


@admin_router.post("/documents")
@operation_log("攻略库", "上传文档")
def create_document(payload: GuideDocumentCreateRequest, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    text = guide_service.parse_file(payload.file_path)
    return Result(data=guide_service.create_document(db, payload.title, payload.file_path, payload.doc_type, payload.destination, text))


@admin_router.get("/documents/{document_id}/chunks")
def get_chunks(document_id: int, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    return Result(data=guide_service.get_chunks(db, document_id))


@admin_router.delete("/documents/{document_id}")
@operation_log("攻略库", "删除文档")
def delete_document(document_id: int, request: Request, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    guide_service.delete_document(db, document_id)
    return Result()
