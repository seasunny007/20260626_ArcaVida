import pytest

from config.settings import Settings


def test_production_requires_non_default_hash_salt() -> None:
    settings = Settings(environment="production", source_chat_hash_salt="arcavida-local-salt")

    with pytest.raises(RuntimeError, match="SOURCE_CHAT_HASH_SALT"):
        settings.validate_runtime_security()


def test_webhook_requires_secret_path() -> None:
    settings = Settings(webhook_url="https://example.test/webhook")

    with pytest.raises(RuntimeError, match="WEBHOOK_SECRET_PATH"):
        settings.validate_runtime_security()


def test_operator_chat_id_set_parses_csv() -> None:
    settings = Settings(operator_chat_ids="123, 456, ")

    assert settings.operator_chat_id_set() == {"123", "456"}
