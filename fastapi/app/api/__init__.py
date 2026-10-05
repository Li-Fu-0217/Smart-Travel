"""API 路由汇总，前缀 /api（见施工规范 §3、§4.5）。"""
from fastapi import APIRouter

from app.api import auth

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
