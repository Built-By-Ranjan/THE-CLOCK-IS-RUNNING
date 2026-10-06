import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "THE CLOCK IS RUNNING"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/the_clock_is_running"
    SECRET_KEY: str = "development-secret-key-at-least-32-bytes-long!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    MFA_ENCRYPTION_KEY: str = ""
    ENVIRONMENT: str = "development"
    GEMINI_API_KEY: str = "replace_me"

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
