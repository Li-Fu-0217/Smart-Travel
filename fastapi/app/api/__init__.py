"""API 路由汇总，前缀 /api（见施工规范 §3、§4.5）。"""
from fastapi import APIRouter

from app.api import alerts, auth, booking, family, files, logs, menus, profile, records, roles, templates, todos, tours, travelers, trips, users

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(menus.router)
api_router.include_router(roles.router)
api_router.include_router(users.router)
api_router.include_router(logs.router)
api_router.include_router(profile.router)
api_router.include_router(files.router)
api_router.include_router(travelers.router)
api_router.include_router(family.router)
api_router.include_router(family.admin_router)
api_router.include_router(trips.router)
api_router.include_router(todos.router)
api_router.include_router(booking.router)
api_router.include_router(booking.admin_router)
api_router.include_router(templates.router)
api_router.include_router(templates.admin_router)
api_router.include_router(tours.router)
api_router.include_router(tours.admin_router)
api_router.include_router(alerts.router)
api_router.include_router(alerts.admin_router)
api_router.include_router(records.router)
api_router.include_router(records.admin_router)
