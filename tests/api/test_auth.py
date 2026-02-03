def test_login_success_and_failure(client):

    ok = client.post("/api/auth/login", json={"username": "alice", "password": "password"})
    assert ok.status_code == 200
    assert ok.json()["role"] == "USER"

    ng = client.post("/api/auth/login", json={"username": "alice", "password": "wrong"})
    assert ng.status_code == 401
