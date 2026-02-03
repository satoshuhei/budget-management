from decimal import Decimal

from app.application.dto import PlanBulkCreate, PlanCreate
from app.application.usecases import create_plans_bulk


def test_bulk_plan_import(uow_sqlite):
    bulk = PlanBulkCreate(
        plans=[
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
                note="bulk",
            ),
            PlanCreate(
                fiscal_year=2026,
                department_id=1,
                category_id=12,
                subcategory_id=13,
                product_name="Service B",
                vendor="Vendor Y",
                planned_month="2026-05",
                contract_type="年額",
                amount=Decimal("2400"),
                plan_type="保守",
                note="bulk",
            ),
        ]
    )

    created = create_plans_bulk(uow_sqlite, bulk)
    assert len(created) == 2
    assert created[0].product_name == "Service A"
