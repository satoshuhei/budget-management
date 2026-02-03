from decimal import Decimal

from app.application.dto import BudgetAdjustmentCreate, BudgetCreate, PlanCreate
from app.application.usecases import adjust_budget, create_budget, create_plan, dashboard_summary, list_plans


def test_dashboard_summary_and_plan_list(uow_sqlite):
    budget = create_budget(
        uow_sqlite,
        BudgetCreate(fiscal_year=2026, department_id=1, category_id=10, initial_amount=Decimal("1000")),
    )
    adjust_budget(
        uow_sqlite,
        budget.id,
        BudgetAdjustmentCreate(amount=Decimal("200"), reason="adjust", created_by="admin"),
    )

    create_plan(
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
    create_plan(
        uow_sqlite,
        PlanCreate(
            fiscal_year=2026,
            department_id=2,
            category_id=10,
            subcategory_id=11,
            product_name="Service B",
            vendor="Vendor Y",
            planned_month="2026-05",
            contract_type="月額",
            amount=Decimal("500"),
            plan_type="サブスク",
            note="other",
        ),
    )

    summary = dashboard_summary(uow_sqlite, fiscal_year=2026, department_id=1)
    assert summary["budget_total"] == Decimal("1200")
    assert summary["plan_total"] == Decimal("300")

    plans = list_plans(uow_sqlite, fiscal_year=2026, department_id=1)
    assert len(plans) == 1
    assert plans[0].product_name == "Service A"
