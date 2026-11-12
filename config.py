from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:1234@localhost:5432/brujulaj_db"
    debug: bool = False
    anthropic_api_key: str = ""
    secret_key: str = "dev_insecure_fallback_key"
    encryption_key: str = ""  # clave para cifrar datos sensibles en reposo (cédula)
    allowed_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
