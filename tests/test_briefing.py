from datetime import datetime, timezone

from core.briefing import generate_briefing
from models.schemas import RecordStatus, RescueRecord


def make_record(priority: int, location: str, trapped: bool = False) -> RescueRecord:
    return RescueRecord(
        id=f"id-{priority}-{location}",
        raw_text="raw",
        detected_lang="zh",
        translated_text="translated",
        location=location,
        needs=["水"],
        trapped=trapped,
        priority=priority,
        slang_alert=False,
        slang_hint=None,
        status=RecordStatus.pending,
        volunteer_notes="",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        source_chat_id="hashed",
    )


def test_generate_briefing_sorts_and_summarizes() -> None:
    briefing = generate_briefing([make_record(1, "A"), make_record(3, "B", trapped=True)])

    assert briefing.splitlines()[1].startswith("[高]")
    assert "高优先级 1" in briefing
    assert "被困 1" in briefing
