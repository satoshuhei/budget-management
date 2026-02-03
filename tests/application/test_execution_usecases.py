from decimal import Decimal

import pytest

from app.application.dto import ExecutionCreate, ExecutionPaid, PlanCreate, RequestCreate, BudgetCreate
from app.application.usecases import (
    approve_request,
    create_budget,
    create_execution,
    create_plan,
    create_request,
    mark_execution_paid,
    set_execution_status,
    submit_request,
)
from app.domain.enums import ExecutionStatus
from app.domain.errors import BudgetOverrun


def test_execution_paid_creates_actualize_and_uncommit(uow_sqlite):
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

    execution = create_execution(uow_sqlite, ExecutionCreate(request_id=request.id))
    set_execution_status(uow_sqlite, execution.id, ExecutionStatus.ORDERED)
    set_execution_status(uow_sqlite, execution.id, ExecutionStatus.DELIVERED)
    set_execution_status(uow_sqlite, execution.id, ExecutionStatus.INVOICED)

    mark_execution_paid(
        uow_sqlite,
        execution.id,
        ExecutionPaid(actual_amount=Decimal("250"), allow_over=False, reason="paid", paid_by="accounting"),
    )

    with uow_sqlite:
        totals = uow_sqlite.transactions.totals_for_budget(budget.id)
    assert totals["actual"] == Decimal("250")
    assert totals["commit"] == Decimal("50")


def test_execution_paid_overrun_raises(uow_sqlite):
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
    approve_request(uow_sqlite, request.id, reason="ok", approved_by="approver")

    execution = create_execution(uow_sqlite, ExecutionCreate(request_id=request.id))
    set_execution_status(uow_sqlite, execution.id, ExecutionStatus.ORDERED)
    set_execution_status(uow_sqlite, execution.id, ExecutionStatus.DELIVERED)
    set_execution_status(uow_sqlite, execution.id, ExecutionStatus.INVOICED)

    with pytest.raises(BudgetOverrun):
        mark_execution_paid(
            uow_sqlite,
            execution.id,
            ExecutionPaid(actual_amount=Decimal("400"), allow_over=False, reason="paid", paid_by="accounting"),
        )
