from pathlib import Path

from config.settings import get_settings
from core.material_manager import (
    material_dashboard,
    material_map_markers,
    record_delivery,
    report_need,
    sanitized_export,
)
from models.database import create_distribution_point, list_material_needs
from models.schemas import (
    DeliveryRecordCreate,
    DistributionPointCreate,
    MaterialNeedCreate,
    MaterialType,
    MaterialUrgency,
)


def configure_test_env(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'arca_vida.db'}")
    get_settings.cache_clear()


def test_material_flow_updates_stock_map_export_and_audit(monkeypatch, tmp_path: Path) -> None:
    configure_test_env(monkeypatch, tmp_path)

    point_id = create_distribution_point(
        DistributionPointCreate(
            name="Centro Comunitario",
            lat=10.5,
            lng=-66.9,
            contact_person="Private Name",
            contact_channel="private-phone",
            population_served=100,
        )
    )
    need_id = report_need(
        MaterialNeedCreate(
            point_id=point_id,
            material_type=MaterialType.water,
            quantity=200,
            current_stock=10,
            unit="boxes",
            urgency=MaterialUrgency.critical,
            reported_by="Private Reporter",
            reported_channel="private-chat",
        )
    )
    record_delivery(
        DeliveryRecordCreate(
            point_id=point_id,
            material_type=MaterialType.water,
            quantity=50,
            unit="boxes",
            delivered_by="Private Driver",
            notes="private route",
        )
    )

    needs = list_material_needs(point_id=point_id)
    assert needs[0].id == need_id
    assert needs[0].current_stock == 60

    dashboard = material_dashboard()
    assert dashboard["summary"]["points"] == 1
    assert dashboard["summary"]["deliveries"] == 1
    assert dashboard["needs"][0]["shortage_index"] > 60

    markers = material_map_markers()
    assert markers[0]["color"] == "red"
    assert markers[0]["contact_person"] is None
    assert markers[0]["contact_channel"] is None

    exported = sanitized_export()
    assert exported["distribution_points"][0]["contact_person"] is None
    assert exported["delivery_records"][0]["delivered_by"] is None
    assert exported["delivery_records"][0]["notes"] is None
    assert len(exported["audit_events"]) == 3
