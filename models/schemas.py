from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class RecordStatus(StrEnum):
    pending = "pending"
    verified = "verified"
    dispatched = "dispatched"
    closed = "closed"


class DistributionPointStatus(StrEnum):
    active = "ACTIVE"
    full = "FULL"
    closed = "CLOSED"


class MaterialType(StrEnum):
    water = "WATER"
    food = "FOOD"
    hygiene_kit = "HYGIENE_KIT"
    medicine = "MEDICINE"
    tent = "TENT"
    other = "OTHER"


class MaterialUrgency(StrEnum):
    critical = "CRITICAL"
    high = "HIGH"
    medium = "MEDIUM"
    low = "LOW"


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


class DistributionPointCreate(BaseModel):
    name: str
    lat: float | None = None
    lng: float | None = None
    contact_person: str | None = None
    contact_channel: str | None = None
    population_served: int | None = None
    status: DistributionPointStatus = DistributionPointStatus.active


class DistributionPoint(DistributionPointCreate):
    id: str
    created_at: datetime
    updated_at: datetime


class MaterialNeedCreate(BaseModel):
    point_id: str
    material_type: MaterialType
    quantity: int
    current_stock: int = 0
    unit: str = "units"
    urgency: MaterialUrgency = MaterialUrgency.medium
    reported_by: str | None = None
    reported_channel: str | None = None


class MaterialNeed(MaterialNeedCreate):
    id: str
    updated_at: datetime


class DeliveryRecordCreate(BaseModel):
    point_id: str
    material_type: MaterialType
    quantity: int
    unit: str = "units"
    delivered_by: str | None = None
    notes: str | None = None


class DeliveryRecord(DeliveryRecordCreate):
    id: str
    delivered_at: datetime
    created_at: datetime


class AuditEvent(BaseModel):
    id: str
    action: str
    entity_type: str
    entity_id: str
    details: dict[str, Any]
    created_at: datetime


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


def row_to_distribution_point(row: dict[str, Any]) -> DistributionPoint:
    return DistributionPoint(**row)


def row_to_material_need(row: dict[str, Any]) -> MaterialNeed:
    return MaterialNeed(**row)


def row_to_delivery_record(row: dict[str, Any]) -> DeliveryRecord:
    return DeliveryRecord(**row)


def row_to_audit_event(row: dict[str, Any]) -> AuditEvent:
    import json

    return AuditEvent(**{**row, "details": json.loads(row["details"] or "{}")})
