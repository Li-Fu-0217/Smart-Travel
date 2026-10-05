"""验证码服务：内存存储、5 分钟过期、一次性、大小写不敏感（见施工规范 §4.5）。"""
import base64
import io
import random
import string
import time
import uuid

from PIL import Image, ImageDraw, ImageFont

from app.common.exceptions import BusinessException

_TTL_SECONDS = 300
_store: dict = {}  # captcha_id -> (code_lower, created_at)


def generate() -> dict:
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    captcha_id = uuid.uuid4().hex
    _store[captcha_id] = (code.lower(), time.time())
    return {"captcha_id": captcha_id, "image": _render(code)}


def verify(captcha_id: str, captcha_code: str) -> None:
    entry = _store.get(captcha_id)
    if entry is None:
        raise BusinessException("验证码错误或已过期", code=400)
    del _store[captcha_id]  # 一次性使用：验证后立即删除
    code, created = entry
    if time.time() - created > _TTL_SECONDS:
        raise BusinessException("验证码错误或已过期", code=400)
    if not captcha_code or captcha_code.lower() != code:
        raise BusinessException("验证码错误或已过期", code=400)


def _render(code: str) -> str:
    width, height = 120, 40
    image = Image.new("RGB", (width, height), (242, 245, 249))
    draw = ImageDraw.Draw(image)
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = x1 + random.randint(-25, 25)
        y2 = y1 + random.randint(-12, 12)
        draw.line([(x1, y1), (x2, y2)], fill=(170, 185, 200))
    font = ImageFont.load_default()
    for i, ch in enumerate(code):
        draw.text((15 + i * 25, 12), ch, fill=(45, 65, 95), font=font)
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
