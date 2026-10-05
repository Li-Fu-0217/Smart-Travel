"""业务异常（见施工规范 §4.4）。"""


class BusinessException(Exception):
    """业务异常：code 为业务码；401/403/404 映射到对应 HTTP 状态，其余在 body 中表达。"""

    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)
