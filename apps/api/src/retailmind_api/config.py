"""Typed environment configuration for the RetailMind API."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    web_origin: str = "http://localhost:3000"
    qdrant_url: str = "local:qdrant_storage"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "customer_memory"
    memory_backend: str = "qdrant"
    gemini_api_key: str | None = None
    google_api_key: str | None = None
    gemini_model: str = "gemini-3.1-flash-lite"
    lyzr_api_key: str | None = None
    lyzr_agent_id: str | None = None
    lyzr_api_url: str = "https://agent-prod.studio.lyzr.ai/v3/inference/chat/"
    lyzr_user_id: str = "retailmind-demo"
    ai_timeout_seconds: float = 8.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
