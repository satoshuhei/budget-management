import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def user_headers(client: TestClient):
    response = client.post("/api/auth/login", json={"username": "alice", "password": "password"})
    assert response.status_code == 200
    data = response.json()
    return {"X-User": data["username"], "X-Role": data["role"]}
