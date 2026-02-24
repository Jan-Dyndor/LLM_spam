from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

DOTENV = os.path.join(os.path.dirname(__file__), ".env")
print(DOTENV)


class Settings(BaseSettings):
    google_api_key: SecretStr = Field(..., validation_alias="GEMINI_API_KEY")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()  # type: ignore
print(settings.google_api_key.get_secret_value())
