"""应用配置：从 .env 加载（见施工规范 §4.6）。"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # 服务
    APP_NAME: str = "travel-assistant"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "travel_assistant"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""

    # 鉴权与上传
    JWT_SECRET: str = "change-me-to-a-long-random-string"
    JWT_EXPIRATION_MS: int = 86400000
    UPLOAD_PATH: str = "./uploads"

    # 智能助手
    AGENT_DEMO_MODE: bool = True
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.deepseek.com"
    LLM_MODEL: str = "deepseek-v4-flash"
    LLM_THINKING: str = "disabled"
    LLM_REASONING_EFFORT: str = "high"
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 4096

    # 知识库向量目录
    CHROMA_PATH: str = "./data/chroma"
    KNOWLEDGE_COLLECTION: str = "travel_guide_knowledge"

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    @property
    def upload_root(self) -> Path:
        return Path(self.UPLOAD_PATH).resolve()

    @property
    def chroma_root(self) -> Path:
        return Path(self.CHROMA_PATH).resolve()


settings = Settings()
