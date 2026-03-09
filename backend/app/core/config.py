from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Motorola Community Scanner", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@postgres:5432/motorola_scanner",
        alias="DATABASE_URL",
    )

    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    celery_broker_url: str = Field(default="redis://redis:6379/0", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://redis:6379/0", alias="CELERY_RESULT_BACKEND")

    firecrawl_base_url: AnyHttpUrl = Field(default="https://api.firecrawl.dev", alias="FIRECRAWL_BASE_URL")
    firecrawl_api_key: str = Field(default="changeme", alias="FIRECRAWL_API_KEY")
    ollama_base_url: AnyHttpUrl = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="qwen3:8b", alias="OLLAMA_MODEL")

    motorola_community_url: AnyHttpUrl = Field(
        default="https://forums.lenovo.com/t5/Motorola-Community/ct-p/MotorolaCommunity",
        alias="MOTOROLA_COMMUNITY_URL",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
