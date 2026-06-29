from pathlib import Path

from fastapi.testclient import TestClient

from config.settings import get_settings
from web.app import app


def configure_test_env(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'arca_vida.db'}")
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    get_settings.cache_clear()


def test_web_workstation_creates_record_and_briefing(monkeypatch, tmp_path: Path) -> None:
    configure_test_env(monkeypatch, tmp_path)

    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "ArcaVida 工作台" in response.text
        assert "功能入口" in response.text
        assert "状态统计" in response.text
        assert "物资管理" in response.text
        assert "地图看板" in response.text
        assert "脱敏导出" in response.text
        assert "审计日志" in response.text
        assert "命令说明" in response.text

        created = client.post(
            "/api/records",
            json={
                "raw_text": "Ubicación: Caracas Centro. Hay una familia atrapada, necesita agua.",
                "source_label": "test-web",
            },
        )
        assert created.status_code == 200
        record_id = created.json()["id"]

        records = client.get("/api/records").json()
        assert records[0]["id"] == record_id
        assert records[0]["priority_label"] == "高"

        status = client.get("/api/status").json()
        assert status == {
            "total": 1,
            "pending": 1,
            "verified": 0,
            "dispatched": 0,
            "closed": 0,
        }

        help_text = client.get("/api/help").json()["help"]
        assert "/briefing" in help_text
        assert "/status" in help_text
        assert "/need" in help_text
        assert "/deliver" in help_text
        assert "/shortage" in help_text

        briefing = client.get("/api/briefing").json()["briefing"]
        assert "ArcaVida 求救简报" in briefing


def test_web_workstation_requires_login_when_password_is_set(monkeypatch, tmp_path: Path) -> None:
    configure_test_env(monkeypatch, tmp_path)
    monkeypatch.setenv("ADMIN_PASSWORD", "secret")
    get_settings.cache_clear()

    with TestClient(app) as client:
        assert client.get("/api/records").status_code == 401
        assert client.get("/api/status").status_code == 401
        assert client.get("/api/help").status_code == 401
        assert client.post("/api/login", json={"password": "bad"}).status_code == 401
        assert client.post("/api/login", json={"password": "secret"}).status_code == 200
        assert client.get("/api/records").status_code == 200


def test_web_material_management_map_export_and_audit(monkeypatch, tmp_path: Path) -> None:
    configure_test_env(monkeypatch, tmp_path)

    with TestClient(app) as client:
        point = client.post(
            "/api/material/points",
            json={
                "name": "Centro Comunitario",
                "lat": 10.5,
                "lng": -66.9,
                "contact_person": "Private Name",
                "contact_channel": "private-phone",
                "population_served": 100,
            },
        )
        assert point.status_code == 200
        point_id = point.json()["id"]

        need = client.post(
            "/api/material/needs",
            json={
                "point_id": point_id,
                "material_type": "WATER",
                "quantity": 200,
                "current_stock": 10,
                "unit": "boxes",
                "urgency": "CRITICAL",
            },
        )
        assert need.status_code == 200

        delivery = client.post(
            "/api/material/deliveries",
            json={
                "point_id": point_id,
                "material_type": "WATER",
                "quantity": 50,
                "unit": "boxes",
                "delivered_by": "Private Driver",
                "notes": "private route",
            },
        )
        assert delivery.status_code == 200

        dashboard = client.get("/api/material/dashboard").json()
        assert dashboard["summary"]["points"] == 1
        assert dashboard["summary"]["deliveries"] == 1
        assert dashboard["needs"][0]["need"]["current_stock"] == 60

        markers = client.get("/api/material/map").json()
        assert markers[0]["color"] == "red"
        assert markers[0]["contact_person"] is None

        exported = client.get("/api/export/sanitized").json()
        assert exported["distribution_points"][0]["contact_channel"] is None
        assert exported["delivery_records"][0]["delivered_by"] is None

        audit = client.get("/api/audit").json()
        assert [event["entity_type"] for event in audit] == [
            "delivery_record",
            "material_need",
            "distribution_point",
        ]
