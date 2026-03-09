import os

from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///./phase2_test.db"

from app.main import app  # noqa: E402


def test_start_scan_uses_fixed_motorola_source(monkeypatch) -> None:
    called = {"value": False}

    def fake_send_task(name: str, args: list[int]):
        called["value"] = True
        assert name == "app.workers.tasks.run_scan_execution"
        assert len(args) == 1
        return None

    monkeypatch.setattr("app.services.scan_service.celery_app.send_task", fake_send_task)

    with TestClient(app) as client:
        response = client.post("/api/v1/scan/start")

    assert response.status_code == 202
    payload = response.json()
    assert called["value"] is True
    assert payload["scan_execution"]["source_url"] == "https://forums.lenovo.com/t5/Motorola-Community/ct-p/MotorolaCommunity"
    assert payload["scan_execution"]["status"] == "queued"


def test_latest_scan_returns_last_execution(monkeypatch) -> None:
    monkeypatch.setattr("app.services.scan_service.celery_app.send_task", lambda *_args, **_kwargs: None)

    with TestClient(app) as client:
        start_response = client.post("/api/v1/scan/start")
        latest_response = client.get("/api/v1/scan/latest")

    assert start_response.status_code == 202
    assert latest_response.status_code == 200
    assert latest_response.json() is not None
    assert latest_response.json()["id"] == start_response.json()["scan_execution"]["id"]

