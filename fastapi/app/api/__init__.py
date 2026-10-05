"""API 路由汇总，前缀 /api（见施工规范 §3、§4.5）。"""
from fastapi import APIRouter

from app.api import auth, logs, menus, roles, users

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(menus.router)
api_router.include_router(roles.router)
api_router.include_router(users.router)
api_router.include_router(logs.router)
