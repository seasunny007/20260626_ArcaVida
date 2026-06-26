from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class RecordStatus(StrEnum):
    pending = "pending"
    verified = "verified"
    dispatched = "dispatched"
    closed = "closed"


class ExtractedInfo(BaseModel):
    location: str = ""
    needs: list[str] = Field(default_factory=list)
    trapped: bool = False
    priority: str = "low"
    slang_alert: bool = False
    slang_meaning: str | None = None


class RescueRecordCreate(BaseModel):
    raw_text: str
    detected_lang: str
    translated_text: str
    location: str = ""
    needs: list[str] = Field(default_factory=list)
    trapped: bool = False
    priority: int = 1
    slang_alert: bool = False
    slang_hint: str | None = None
    source_chat_id: str


class RescueRecord(BaseModel):
    id: str
    raw_text: str
    detected_lang: str
    translated_text: str
    location: str
    needs: list[str]
    trapped: bool
    priority: int
    slang_alert: bool
    slang_hint: str | None
    status: RecordStatus
    volunteer_notes: str
    created_at: datetime
    updated_at: datetime
    source_chat_id: str


def priority_to_int(priority: str | int) -> int:
    if isinstance(priority, int):
        return max(1, min(priority, 3))
    return {"low": 1, "medium": 2, "high": 3}.get(priority.lower(), 1)


def row_to_record(row: dict[str, Any]) -> RescueRecord:
    import json

    return RescueRecord(
        **{
            **row,
            "needs": json.loads(row["needs"] or "[]"),
            "trapped": bool(row["trapped"]),
            "slang_alert": bool(row["slang_alert"]),
        }
    )
