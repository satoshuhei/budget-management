from decimal import Decimal

import pytest

from app.application.dto import BudgetCreate, PlanCreate, RequestCreate
from app.application.usecases import (
    approve_request,
    create_budget,
    create_plan,
    create_request,
    submit_request,
)
from app.domain.errors import BudgetOverrun


def test_request_approval_creates_commit_transaction(uow_sqlite):
    budget = create_budget(
        uow_sqlite,
        BudgetCreate(fiscal_year=2026, department_id=1, category_id=10, initial_amount=Decimal("1000")),
    )

    plan = create_plan(
        uow_sqlite,
        PlanCreate(
            fiscal_year=2026,
            department_id=1,
            category_id=10,
            subcategory_id=11,
            product_name="Service A",
            vendor="Vendor X",
            planned_month="2026-04",
            contract_type="月額",
            amount=Decimal("300"),
            plan_type="サブスク",
            note="first",
        ),
    )

    request = create_request(
        uow_sqlite,
        RequestCreate(plan_id=plan.id, requested_amount=Decimal("300"), created_by="alice", reason="plan"),
    )
    submit_request(uow_sqlite, request.id)
    approve_request(uow_sqlite, request.id, reason="ok", approved_by="approver")

    with uow_sqlite:
        totals = uow_sqlite.transactions.totals_for_budget(budget.id)
    assert totals["commit"] == Decimal("300")


def test_request_approval_fails_when_budget_insufficient(uow_sqlite):
    create_budget(
        uow_sqlite,
        BudgetCreate(fiscal_year=2026, department_id=1, category_id=10, initial_amount=Decimal("100")),
    )

    plan = create_plan(
        uow_sqlite,
        PlanCreate(
            fiscal_year=2026,
            department_id=1,
            category_id=10,
            subcategory_id=11,
            product_name="Service A",
            vendor="Vendor X",
            planned_month="2026-04",
            contract_type="月額",
            amount=Decimal("300"),
            plan_type="サブスク",
            note="first",
        ),
    )

    request = create_request(
        uow_sqlite,
        RequestCreate(plan_id=plan.id, requested_amount=Decimal("300"), created_by="alice", reason="plan"),
    )
    submit_request(uow_sqlite, request.id)

    with pytest.raises(BudgetOverrun):
        approve_request(uow_sqlite, request.id, reason="over", approved_by="approver")
