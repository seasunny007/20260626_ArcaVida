import pytest

from config.settings import get_settings
from core.translator import detect_language, translate_text


def test_detect_language() -> None:
    assert detect_language("需要水") == "zh"
    assert detect_language("necesita agua") == "es"


@pytest.mark.asyncio
async def test_translate_without_credentials_returns_original_text() -> None:
    result = await translate_text("necesita agua")

    assert result.detected_lang == "es"
    assert result.translated_text == "necesita agua"


@pytest.mark.asyncio
async def test_unknown_translation_provider_returns_original_text(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "translation_provider", "none")

    result = await translate_text("necesita agua")

    assert result.detected_lang == "es"
    assert result.translated_text == "necesita agua"
