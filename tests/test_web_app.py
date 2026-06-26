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

        briefing = client.get("/api/briefing").json()["briefing"]
        assert "ArcaVida 求救简报" in briefing


def test_web_workstation_requires_login_when_password_is_set(monkeypatch, tmp_path: Path) -> None:
    configure_test_env(monkeypatch, tmp_path)
    monkeypatch.setenv("ADMIN_PASSWORD", "secret")
    get_settings.cache_clear()

    with TestClient(app) as client:
        assert client.get("/api/records").status_code == 401
        assert client.post("/api/login", json={"password": "bad"}).status_code == 401
        assert client.post("/api/login", json={"password": "secret"}).status_code == 200
        assert client.get("/api/records").status_code == 200
