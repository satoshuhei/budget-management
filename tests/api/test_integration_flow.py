from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def login_headers(client: TestClient, username: str, password: str) -> dict[str, str]:
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    data = response.json()
    return {"X-User": data["username"], "X-Role": data["role"]}


def test_integration_flow_simple():
    client = TestClient(app)
    admin_headers = login_headers(client, "admin", "admin")

    health = client.get("/health")
    assert health.status_code == 200

    suffix = uuid4().hex[:8]
    category_name = f"統合テスト-{suffix}"
    subcategory_name = f"小分類-{suffix}"

    category_res = client.post("/api/categories", json={"name": category_name}, headers=admin_headers)
    assert category_res.status_code == 200
    category_id = category_res.json()["id"]

    sub_res = client.post(
        "/api/subcategories",
        json={"category_id": category_id, "name": subcategory_name},
        headers=admin_headers,
    )
    assert sub_res.status_code == 200
    subcategory_id = sub_res.json()["id"]

    list_categories = client.get("/api/categories", headers=admin_headers)
    assert list_categories.status_code == 200
    assert any(c["id"] == category_id for c in list_categories.json())

    list_subcategories = client.get("/api/subcategories", headers=admin_headers)
    assert list_subcategories.status_code == 200
    assert any(s["id"] == subcategory_id for s in list_subcategories.json())

    budget_res = client.post(
        "/api/budgets",
        json={
            "fiscal_year": 2026,
            "department_id": 1,
            "category_id": category_id,
            "initial_amount": 2000000,
        },
        headers=admin_headers,
    )
    assert budget_res.status_code == 200

    plan_res = client.post(
        "/api/plans",
        json={
            "fiscal_year": 2026,
            "department_id": 1,
            "category_id": category_id,
            "subcategory_id": subcategory_id,
            "product_name": "統合テスト計画",
            "vendor": "TestVendor",
            "planned_month": "2026-04",
            "contract_type": "スポット",
            "amount": 500000,
            "plan_type": "OPEX",
            "note": "integration",
        },
        headers=admin_headers,
    )
    assert plan_res.status_code == 200
    plan_id = plan_res.json()["id"]

    update_res = client.put(
        f"/api/plans/{plan_id}",
        json={
            "category_id": category_id,
            "subcategory_id": subcategory_id,
            "product_name": "統合テスト計画-更新",
            "vendor": "TestVendor",
            "planned_month": "2026-05",
            "contract_type": "スポット",
            "amount": 600000,
            "plan_type": "OPEX",
            "note": "updated",
            "status": "ACTIVE",
            "changed_by": "admin",
            "reason": "integration",
        },
        headers=admin_headers,
    )
    assert update_res.status_code == 200

    changes_res = client.get(f"/api/plans/{plan_id}/changes", headers=admin_headers)
    assert changes_res.status_code == 200

    request_res = client.post(
        "/api/requests",
        json={
            "plan_id": plan_id,
            "requested_amount": 300000,
            "created_by": "admin",
            "reason": "integration",
        },
        headers=admin_headers,
    )
    assert request_res.status_code == 200
    request_id = request_res.json()["id"]

    submit_res = client.post(f"/api/requests/{request_id}/submit", headers=admin_headers)
    assert submit_res.status_code == 200

    inbox_res = client.get("/api/approvals/inbox", headers=admin_headers)
    assert inbox_res.status_code == 200

    approve_res = client.post(
        f"/api/approvals/{request_id}/approve",
        params={"reason": "ok", "approved_by": "admin"},
        headers=admin_headers,
    )
    assert approve_res.status_code == 200

    execution_res = client.post(
        "/api/executions",
        json={"request_id": request_id},
        headers=admin_headers,
    )
    assert execution_res.status_code == 200
    execution_id = execution_res.json()["id"]

    for action in ("set-ordered", "set-delivered", "set-invoiced"):
        status_res = client.post(f"/api/executions/{execution_id}/{action}", headers=admin_headers)
        assert status_res.status_code == 200

    paid_res = client.post(
        f"/api/executions/{execution_id}/set-paid",
        json={"actual_amount": 280000, "allow_over": False, "reason": "paid", "paid_by": "admin"},
        headers=admin_headers,
    )
    assert paid_res.status_code == 200

    list_plans = client.get("/api/plans", headers=admin_headers)
    assert list_plans.status_code == 200

    list_requests = client.get("/api/requests", headers=admin_headers)
    assert list_requests.status_code == 200

    list_executions = client.get("/api/executions", headers=admin_headers)
    assert list_executions.status_code == 200

    dashboard = client.get("/api/dashboard/summary", params={"fiscal_year": 2026, "department_id": 1}, headers=admin_headers)
    assert dashboard.status_code == 200

    report_budget = client.get(
        "/api/reports/budget-summary",
        params={"fiscal_year": 2026, "department_id": 1},
        headers=admin_headers,
    )
    assert report_budget.status_code == 200

    report_month = client.get(
        "/api/reports/monthly-summary",
        params={"fiscal_year": 2026, "department_id": 1},
        headers=admin_headers,
    )
    assert report_month.status_code == 200

    unplanned = client.get("/api/reports/unplanned-requests", headers=admin_headers)
    assert unplanned.status_code == 200

    audit_logs = client.get("/api/audit-logs/recent", headers=admin_headers)
    assert audit_logs.status_code == 200
