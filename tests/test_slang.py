from core.slang_matcher import format_slang_hint, match_slang


def test_match_slang_handles_accents() -> None:
    matches = match_slang("Hay frio y falta pan")

    assert {match.term for match in matches} >= {"frio", "pan"}
    assert "冲突" in (format_slang_hint(matches) or "")
