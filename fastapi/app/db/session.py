"""数据库引擎与会话（见施工规范 §4.3）。"""
from sqlmodel import create_engine

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, echo=False)
