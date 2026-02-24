from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


root = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    google_api_key: SecretStr = Field(..., validation_alias="GEMINI_API_KEY")

    model_config = SettingsConfigDict(env_file=root / ".env", env_file_encoding="utf-8")


settings = Settings()  # type: ignore
print(settings.google_api_key.get_secret_value())
