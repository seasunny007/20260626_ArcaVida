from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    telegram_token: str | None = None
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_model: str = "gpt-3.5-turbo"
    translation_provider: str = "llm"
    google_application_credentials: str | None = None
    database_url: str = "sqlite:///./arca_vida.db"
    webhook_url: str | None = None
    webhook_secret_path: str | None = None
    log_level: str = "INFO"
    source_chat_hash_salt: str = "arcavida-local-salt"
    operator_chat_ids: str = ""
    admin_password: str | None = None
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def sqlite_path(self, url: str) -> Path:
        if not url.startswith("sqlite:///"):
            raise ValueError("Only sqlite:/// URLs are supported in the MVP")
        return Path(url.removeprefix("sqlite:///")).expanduser()

    def operator_chat_id_set(self) -> set[str]:
        return {item.strip() for item in self.operator_chat_ids.split(",") if item.strip()}

    def validate_runtime_security(self) -> None:
        if (
            self.environment.lower() == "production"
            and self.source_chat_hash_salt == "arcavida-local-salt"
        ):
            raise RuntimeError("SOURCE_CHAT_HASH_SALT must be changed before production startup")
        if self.webhook_url and not self.webhook_secret_path:
            raise RuntimeError("WEBHOOK_SECRET_PATH is required when WEBHOOK_URL is set")
        if self.environment.lower() == "production" and not self.admin_password:
            raise RuntimeError("ADMIN_PASSWORD is required before production startup")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
