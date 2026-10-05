"""上传分类白名单（见施工规范 §4.7）。"""
from app.common.exceptions import BusinessException

AVATAR = "avatar"
COMMON = "common"

# 分类定义：大小上限（字节）与允许扩展名，阶段 2 的 file_service 校验时使用
MAX_SIZE = {
    AVATAR: 2 * 1024 * 1024,
    COMMON: 10 * 1024 * 1024,
}

ALLOWED_EXTENSIONS = {
    AVATAR: {"jpg", "jpeg", "png", "webp"},
    COMMON: {"jpg", "jpeg", "png", "webp", "pdf", "txt", "md"},
}

_ALLOWED = frozenset({AVATAR, COMMON})


def normalize(category):
    """None 或空值归一化为 common；非法分类抛 BusinessException。"""
    if not category:
        return COMMON
    if category not in _ALLOWED:
        raise BusinessException("不支持的上传分类", code=400)
    return category
