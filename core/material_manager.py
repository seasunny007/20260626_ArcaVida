from typing import Any

from models.database import (
    create_delivery_record,
    create_distribution_point,
    create_material_need,
    list_audit_events,
    list_delivery_records,
    list_distribution_points,
    list_material_needs,
)
from models.schemas import (
    DeliveryRecordCreate,
    DistributionPoint,
    DistributionPointCreate,
    MaterialNeed,
    MaterialNeedCreate,
)


def calculate_shortage_index(need: MaterialNeed, point: DistributionPoint) -> float:
    daily_per_person = {
        "WATER": 2.0,
        "FOOD": 0.5,
        "HYGIENE_KIT": 0.05,
        "MEDICINE": 0.02,
        "TENT": 0.01,
    }
    served = max(point.population_served or 0, 0)
    daily_need = served * daily_per_person.get(str(need.material_type), 0.1)
    if daily_need <= 0:
        base = 50.0 if need.quantity > need.current_stock else 0.0
    else:
        days_remaining = max(need.current_stock, 0) / daily_need
        base = max(0.0, 100.0 - (days_remaining / 3.0 * 100.0))

    urgency_factor = {
        "CRITICAL": 1.2,
        "HIGH": 1.1,
        "MEDIUM": 1.0,
        "LOW": 0.8,
    }.get(str(need.urgency), 1.0)
    quantity_gap = max(0, need.quantity - need.current_stock)
    if quantity_gap <= 0:
        base = min(base, 15.0)
    return round(min(100.0, max(0.0, base * urgency_factor)), 1)


def shortage_color(index: float) -> str:
    if index > 60:
        return "red"
    if index >= 20:
        return "yellow"
    return "green"


def create_point(data: DistributionPointCreate) -> str:
    return create_distribution_point(data)


def report_need(data: MaterialNeedCreate) -> str:
    return create_material_need(data)


def record_delivery(data: DeliveryRecordCreate) -> str:
    return create_delivery_record(data)


def material_dashboard() -> dict[str, Any]:
    points = list_distribution_points()
    needs = list_material_needs()
    deliveries = list_delivery_records()
    point_by_id = {point.id: point for point in points}
    ranked_needs = []
    for need in needs:
        point = point_by_id.get(need.point_id)
        if not point:
            continue
        index = calculate_shortage_index(need, point)
        ranked_needs.append(
            {
                "need": need.model_dump(mode="json"),
                "point": sanitize_point(point),
                "shortage_index": index,
                "color": shortage_color(index),
            }
        )
    ranked_needs.sort(key=lambda item: item["shortage_index"], reverse=True)
    return {
        "points": [sanitize_point(point) for point in points],
        "needs": ranked_needs,
        "deliveries": [delivery.model_dump(mode="json") for delivery in deliveries],
        "summary": {
            "points": len(points),
            "needs": len(needs),
            "deliveries": len(deliveries),
            "critical_needs": sum(1 for item in ranked_needs if item["shortage_index"] > 60),
            "today_delivered": sum(delivery.quantity for delivery in deliveries),
        },
    }


def material_map_markers() -> list[dict[str, Any]]:
    dashboard = material_dashboard()
    point_needs: dict[str, list[dict[str, Any]]] = {}
    for item in dashboard["needs"]:
        point_needs.setdefault(item["point"]["id"], []).append(item)

    markers = []
    for point in dashboard["points"]:
        needs = point_needs.get(point["id"], [])
        top_index = max((item["shortage_index"] for item in needs), default=0.0)
        markers.append(
            {
                **point,
                "shortage_index": top_index,
                "color": shortage_color(top_index),
                "needs": [item["need"] for item in needs],
            }
        )
    return markers


def sanitized_export() -> dict[str, Any]:
    dashboard = material_dashboard()
    return {
        "distribution_points": dashboard["points"],
        "material_needs": dashboard["needs"],
        "delivery_records": [sanitize_delivery(delivery) for delivery in list_delivery_records()],
        "audit_events": [event.model_dump(mode="json") for event in list_audit_events()],
    }


def audit_summary() -> list[dict[str, Any]]:
    return [event.model_dump(mode="json") for event in list_audit_events()]


def sanitize_point(point: DistributionPoint) -> dict[str, Any]:
    data = point.model_dump(mode="json")
    data["contact_person"] = None
    data["contact_channel"] = None
    return data


def sanitize_delivery(delivery: Any) -> dict[str, Any]:
    data = delivery.model_dump(mode="json")
    data["delivered_by"] = None
    data["notes"] = None
    return data
