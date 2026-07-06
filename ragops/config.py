from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    database_url: str = "sqlite:///./data/ragops.db"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "ragops_chunks"
    mlflow_tracking_uri: str = "http://localhost:5000"
    enable_mlflow: bool = False
    embedding_dim: int = 384

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
