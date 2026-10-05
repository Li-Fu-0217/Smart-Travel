"""Pydantic 校验错误翻译成中文（见施工规范 §4.4）。"""
from typing import Dict, List

# 字段名 → 中文名映射表
FIELD_NAMES: Dict[str, str] = {
    "username": "用户名",
    "password": "密码",
    "email": "邮箱",
    "name": "姓名",
    "phone": "手机号",
    "title": "标题",
    "message": "内容",
}


def _translate_error(err: dict) -> str:
    loc = err.get("loc", [])
    field = str(loc[-1]) if loc else "字段"
    field_cn = FIELD_NAMES.get(field, field)
    err_type = err.get("type", "")
    ctx = err.get("ctx", {})

    if err_type == "missing":
        return f"{field_cn}不能为空"
    if "too_long" in err_type:
        limit = ctx.get("max_length", "")
        return f"{field_cn}长度不能超过{limit}个字符"
    if "too_short" in err_type:
        limit = ctx.get("min_length", "")
        return f"{field_cn}长度不能少于{limit}个字符"
    if "string_pattern_mismatch" in err_type:
        return f"{field_cn}格式不正确"
    if "value_error" in err_type:
        return f"{field_cn}取值不合法"
    return f"{field_cn}校验未通过"


def translate_validation_errors(errors: List[dict]) -> str:
    """把 FastAPI RequestValidationError 的错误列表翻译成第一条中文提示。"""
    if not errors:
        return "参数校验失败"
    return _translate_error(errors[0])
