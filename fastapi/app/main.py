"""应用入口（见施工规范 §4.4）。"""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.api import api_router
from app.common.exceptions import BusinessException
from app.common.result import Result
from app.common.validation import translate_validation_errors
from app.core.config import settings

logger = logging.getLogger("travel_assistant")

app = FastAPI(title="智慧旅游智能助手系统")
app.include_router(api_router)

settings.upload_root.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(settings.upload_root)), name="uploads")


@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    http_status = exc.code if exc.code in (401, 403, 404) else 200
    return JSONResponse(
        status_code=http_status,
        content=Result(code=exc.code, message=exc.message).model_dump(by_alias=True),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    msg = translate_validation_errors(exc.errors())
    return JSONResponse(
        status_code=400,
        content=Result(code=400, message=msg).model_dump(by_alias=True),
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.exception("数据库异常")
    msg = "数据库连接失败"
    if isinstance(exc, OperationalError) and "Access denied" in str(exc):
        msg = "数据库连接失败：账号或密码错误"
    return JSONResponse(
        status_code=503,
        content=Result(code=503, message=msg).model_dump(by_alias=True),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("未处理异常")
    return JSONResponse(
        status_code=500,
        content=Result(code=500, message="服务器内部错误").model_dump(by_alias=True),
    )
