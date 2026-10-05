"""文件服务（见施工规范 §4.8、§4.7）。"""
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile

from app.common.exceptions import BusinessException
from app.common.file_categories import ALLOWED_EXTENSIONS, MAX_SIZE, normalize
from app.core.config import settings
from app.models import SysUser
from app.schemas.file import FileVO


def upload(file: UploadFile, category: str) -> FileVO:
    category = normalize(category)
    filename = file.filename or ""
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext not in ALLOWED_EXTENSIONS[category]:
        raise BusinessException("不支持的文件类型", code=400)
    content = file.file.read()
    if len(content) > MAX_SIZE[category]:
        raise BusinessException("文件大小超出限制", code=400)
    yyyymm = datetime.now().strftime("%Y%m")
    dest_dir = settings.upload_root / category / yyyymm
    dest_dir.mkdir(parents=True, exist_ok=True)
    stored = f"{uuid.uuid4().hex}{('.' + ext) if ext else ''}"
    dest = dest_dir / stored
    dest.write_bytes(content)
    rel = dest.relative_to(settings.upload_root)
    path = "/uploads/" + rel.as_posix()
    return FileVO(path=path, name=filename, size=len(content), category=category)


def resolve_path(path: str) -> Path:
    if not path.startswith("/uploads/"):
        raise BusinessException("路径不合法", code=400)
    rel = path[len("/uploads/"):]
    abs_path = (settings.upload_root / rel).resolve()
    if not abs_path.is_relative_to(settings.upload_root.resolve()):
        raise BusinessException("路径不合法", code=400)
    return abs_path


def get_file_path(path: str) -> Path:
    abs_path = resolve_path(path)
    if not abs_path.exists() or not abs_path.is_file():
        raise BusinessException("文件不存在", code=404)
    return abs_path


def delete_file(path: str, current_user: SysUser) -> None:
    parts = path.lstrip("/").split("/")
    category = parts[1] if len(parts) > 1 else ""
    if category == "avatar":
        if current_user.avatar != path:
            raise BusinessException("无权删除该文件", code=403)
    else:
        if current_user.role != "ADMIN":
            raise BusinessException("无权删除该文件", code=403)
    abs_path = resolve_path(path)
    if abs_path.exists():
        abs_path.unlink()
