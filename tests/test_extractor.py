import pytest

from config.settings import get_settings
from core.extractor import extract_info, heuristic_extract


def test_heuristic_extract_prioritizes_trapped_cases() -> None:
    result = heuristic_extract("在 Caracas Centro 有人被困，需要 agua 和 comida")

    assert result.priority == "high"
    assert result.trapped is True
    assert "水" in result.needs
    assert "食物" in result.needs


@pytest.mark.asyncio
async def test_extract_info_uses_local_fallback_without_llm() -> None:
    result = await extract_info("地点: Valencia，需要医疗", use_llm=False)

    assert result.priority == "medium"
    assert "医疗" in result.needs


@pytest.mark.asyncio
async def test_extract_info_falls_back_when_llm_fails(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "openai_api_key", "test-key")

    result = await extract_info("有人被困，需要 agua")

    assert result.priority == "high"
