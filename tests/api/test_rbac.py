def test_audit_logs_requires_auditor_role(client, user_headers):
    response = client.get("/api/audit-logs")
    assert response.status_code == 401

    response = client.get("/api/audit-logs", headers=user_headers)
    assert response.status_code == 403
