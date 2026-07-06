from functools import lru_cache

from openai import AsyncOpenAI
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    openai_api_key: SecretStr
    model: str = "gpt-5.5"
    timeout_s: int = 30
    max_input_chars: int = 10_000
    max_retries: int = 1


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_openai_client() -> AsyncOpenAI:
    settings = get_settings()
    return AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value())
