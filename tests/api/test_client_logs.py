from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.settings import settings


def test_client_log_written(tmp_path: Path):
    settings.client_log_path = str(tmp_path / "client-error.log")
    client = TestClient(app)

    response = client.post(
        "/api/client-logs",
        json={
            "message": "boom",
            "stack": "stack",
            "context": "window.error",
            "info": {"page": "/plans"},
            "createdAt": "2026-02-03T00:00:00Z",
        },
    )
    assert response.status_code == 200
    log_path = Path(settings.client_log_path)
    assert log_path.exists()
    content = log_path.read_text(encoding="utf-8")
    assert "boom" in content
    assert "window.error" in content
