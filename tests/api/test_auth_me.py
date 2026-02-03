def test_auth_me_requires_login(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_auth_me_returns_profile(client, user_headers):
    response = client.get("/api/auth/me", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "alice"
    assert data["role"] == "USER"
