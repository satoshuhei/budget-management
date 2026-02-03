from decimal import Decimal

from app.application.dto import PlanCreate, PlanUpdate
from app.application.usecases import create_plan, list_plan_changes, update_plan
from app.domain.enums import PlanStatus


def test_plan_create_and_update_creates_change_history(uow_sqlite):
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
            amount=Decimal("1200"),
            plan_type="サブスク",
            note="initial",
        ),
    )

    updated = update_plan(
        uow_sqlite,
        plan.id,
        PlanUpdate(
            product_name="Service A+",
            vendor="Vendor X",
            planned_month="2026-05",
            contract_type="月額",
            amount=Decimal("1500"),
            plan_type="サブスク",
            note="updated",
            status=PlanStatus.ACTIVE,
            changed_by="alice",
            reason="price change",
        ),
    )

    assert updated is not None
    changes = list_plan_changes(uow_sqlite, plan.id)
    assert len(changes) == 1
    assert changes[0].changed_by == "alice"
