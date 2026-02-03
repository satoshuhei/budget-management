from decimal import Decimal

from app.application.dto import BudgetCreate, ExecutionCreate, ExecutionPaid, PlanCreate, RequestCreate
from app.application.usecases import (
    approve_request,
    create_budget,
    create_execution,
    create_plan,
    create_request,
    list_audit_logs,
    mark_execution_paid,
    report_monthly_summary,
    report_unplanned_requests,
    set_execution_status,
    submit_request,
)
from app.domain.enums import ExecutionStatus


def test_monthly_summary_and_unplanned_report_and_audit(uow_sqlite):
    create_budget(
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
        ExecutionPaid(actual_amount=Decimal("200"), allow_over=False, reason="paid", paid_by="accounting"),
    )

    monthly = report_monthly_summary(uow_sqlite, fiscal_year=2026, department_id=1)
    assert monthly[0]["month"] == "2026-04"
    assert monthly[0]["plan_total"] == Decimal("300")
    assert monthly[0]["actual_total"] == Decimal("200")

    unplanned = report_unplanned_requests(uow_sqlite)
    assert unplanned["count"] == 0

    logs = list_audit_logs(uow_sqlite)
    assert len(logs) > 0
