from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from functools import lru_cache


root = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    gemini_api_key: SecretStr = Field(..., validation_alias="GEMINI_API_KEY")

    model_config = SettingsConfigDict(env_file=root / ".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
