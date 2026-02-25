from functools import lru_cache
from pathlib import Path
from loguru import logger
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

root = Path(__file__).resolve().parents[3]


class AI_Model(BaseModel):
    model_name: str = "gemini-flash-lite-latest"
    temperature: float = 0.2


class Redis(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0


class Settings(BaseSettings):
    gemini_api_key: SecretStr = Field(..., validation_alias="GEMINI_API_KEY")

    model_config = SettingsConfigDict(env_file=root / ".env", env_file_encoding="utf-8")

    ai_model: AI_Model = AI_Model()
    redis: Redis = Redis()


@lru_cache
def get_settings() -> Settings:
    logger.warning("TWORZRE SETTINGS I CZYTAM ENV ")
    return Settings()  # type: ignore
