"""文件接口（见施工规范 §4.8）。"""
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import FileResponse

from app.common.result import Result
from app.core.deps import get_current_user
from app.services import file_service

router = APIRouter(prefix="/files", tags=["文件"])


@router.post("/upload")
def upload(file: UploadFile = File(...), category: str = Form("common"), current_user=Depends(get_current_user)):
    return Result(data=file_service.upload(file, category))


@router.get("/download")
def download(path: str = Query(...), current_user=Depends(get_current_user)):
    file_path = file_service.get_file_path(path)
    return FileResponse(file_path, filename=file_path.name)


@router.get("/preview")
def preview(path: str = Query(...), current_user=Depends(get_current_user)):
    file_path = file_service.get_file_path(path)
    return FileResponse(file_path, content_disposition_type="inline")


@router.delete("")
def delete(path: str = Query(...), current_user=Depends(get_current_user)):
    file_service.delete_file(path, current_user)
    return Result()
