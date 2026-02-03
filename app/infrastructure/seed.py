from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.domain.enums import BudgetTxType, ExecutionStatus, PlanStatus, RequestStatus
from app.infrastructure import models


def seed_sample_data(session: Session) -> None:
    if session.query(models.CategoryModel).first():
        return

    categories = [
        ("IT・システム", ["SaaS", "ハードウェア", "セキュリティ"]),
        ("設備・備品", ["オフィス備品", "施設改修"]),
        ("外注・委託", ["開発委託", "デザイン"]),
        ("教育・研修", ["研修", "資格取得"]),
    ]

    category_models: list[models.CategoryModel] = []
    for name, _subs in categories:
        category_models.append(models.CategoryModel(name=name))
    session.add_all(category_models)
    session.flush()

    category_id_by_name = {model.name: model.id for model in category_models}

    subcategory_models: list[models.SubcategoryModel] = []
    for category_name, subs in categories:
        for sub_name in subs:
            subcategory_models.append(
                models.SubcategoryModel(category_id=category_id_by_name[category_name], name=sub_name)
            )
    session.add_all(subcategory_models)
    session.flush()

    subcategory_id_by_key: dict[int, dict[str, int]] = {}
    for sub in subcategory_models:
        subcategory_id_by_key.setdefault(sub.category_id, {})[sub.name] = sub.id

    budget_models: list[models.BudgetModel] = []
    base_amounts = {
        "IT・システム": Decimal("12000000"),
        "設備・備品": Decimal("8000000"),
        "外注・委託": Decimal("10000000"),
        "教育・研修": Decimal("4000000"),
    }

    for fiscal_year in (2025, 2026):
        for category_name, base in base_amounts.items():
            budget_models.append(
                models.BudgetModel(
                    fiscal_year=fiscal_year,
                    department_id=1,
                    category_id=category_id_by_name[category_name],
                    initial_amount=base + Decimal("500000") * (fiscal_year - 2025),
                )
            )
    session.add_all(budget_models)
    session.flush()

    adjustment_models = [
        models.BudgetAdjustmentModel(
            budget_id=budget_models[0].id,
            amount=Decimal("250000"),
            reason="増額",
            created_by="system",
            created_at=datetime.utcnow(),
        ),
        models.BudgetAdjustmentModel(
            budget_id=budget_models[1].id,
            amount=Decimal("-150000"),
            reason="減額",
            created_by="system",
            created_at=datetime.utcnow(),
        ),
    ]
    session.add_all(adjustment_models)

    budget_id_by_key = {(b.fiscal_year, b.category_id): b.id for b in budget_models}

    plan_templates = [
        ("IT・システム", "SaaS", "CloudCo", "月額", Decimal("1200000"), "OPEX", "クラウド利用"),
        ("IT・システム", "ハードウェア", "DeviceHub", "スポット", Decimal("900000"), "CAPEX", "端末更新"),
        ("IT・システム", "セキュリティ", "SecureInc", "年額", Decimal("1500000"), "OPEX", "セキュリティ対策"),
        ("設備・備品", "オフィス備品", "OfficeMart", "スポット", Decimal("800000"), "CAPEX", "備品更新"),
        ("設備・備品", "施設改修", "BuildWorks", "請負", Decimal("2800000"), "CAPEX", "設備改修"),
        ("外注・委託", "開発委託", "DevPartners", "準委任", Decimal("3500000"), "CAPEX", "開発委託"),
        ("外注・委託", "デザイン", "DesignLab", "請負", Decimal("2200000"), "CAPEX", "デザイン刷新"),
        ("教育・研修", "研修", "EduPro", "スポット", Decimal("600000"), "OPEX", "研修受講"),
    ]

    plans_data: list[tuple[int, str, str, str, str, str, str, Decimal, str, str]] = []
    for fiscal_year in (2025, 2026):
        for month in range(1, 13):
            planned_month = f"{fiscal_year}-{month:02d}"
            for index, (
                category_name,
                subcategory_name,
                vendor,
                contract_type,
                base_amount,
                plan_type,
                product_label,
            ) in enumerate(plan_templates, start=1):
                amount = base_amount + Decimal("5000") * Decimal(month - 1)
                product_name = f"{product_label} {planned_month}-{index:02d}"
                note = "" if index % 2 == 0 else "定例"
                plans_data.append(
                    (
                        fiscal_year,
                        planned_month,
                        category_name,
                        subcategory_name,
                        product_name,
                        vendor,
                        contract_type,
                        amount,
                        plan_type,
                        note,
                    )
                )

    plan_models: list[models.PlanModel] = []
    for (
        fiscal_year,
        planned_month,
        category_name,
        subcategory_name,
        product_name,
        vendor,
        contract_type,
        amount,
        plan_type,
        note,
    ) in plans_data:
        category_id = category_id_by_name[category_name]
        subcategory_id = subcategory_id_by_key[category_id][subcategory_name]
        plan_models.append(
            models.PlanModel(
                fiscal_year=fiscal_year,
                department_id=1,
                category_id=category_id,
                subcategory_id=subcategory_id,
                product_name=product_name,
                vendor=vendor,
                planned_month=planned_month,
                contract_type=contract_type,
                amount=amount,
                plan_type=plan_type,
                note=note,
                status=PlanStatus.ACTIVE.value,
            )
        )
    for index in (5, 11, 17, 23):
        plan_models[index].status = PlanStatus.ARCHIVED.value
    session.add_all(plan_models)
    session.flush()

    plan_change_models = [
        models.PlanChangeModel(
            plan_id=plan_models[0].id,
            changed_by="system",
            reason="seed",
            diff_json=json.dumps({"amount": "1200000", "note": "初期"}, ensure_ascii=False),
            changed_at=datetime.utcnow(),
        )
    ]
    session.add_all(plan_change_models)

    request_definitions = [
        (0, RequestStatus.DRAFT),
        (1, RequestStatus.SUBMITTED),
        (2, RequestStatus.RETURNED),
        (3, RequestStatus.APPROVED),
        (4, RequestStatus.REJECTED),
        (5, RequestStatus.CANCELED),
        (6, RequestStatus.CLOSED),
        (7, RequestStatus.APPROVED),
        (8, RequestStatus.APPROVED),
        (9, RequestStatus.APPROVED),
        (10, RequestStatus.APPROVED),
        (None, RequestStatus.SUBMITTED),
    ]

    request_models: list[models.RequestModel] = []
    for plan_index, status in request_definitions:
        if plan_index is None:
            request_models.append(
                models.RequestModel(
                    plan_id=None,
                    requested_amount=Decimal("900000"),
                    status=status.value,
                )
            )
            continue

        plan = plan_models[plan_index]
        request_models.append(
            models.RequestModel(
                plan_id=plan.id,
                requested_amount=plan.amount,
                status=status.value,
            )
        )
    session.add_all(request_models)
    session.flush()

    execution_models = [
        models.ExecutionModel(
            request_id=request_models[10].id,
            status=ExecutionStatus.NOT_STARTED.value,
            actual_amount=None,
        ),
        models.ExecutionModel(
            request_id=request_models[7].id,
            status=ExecutionStatus.ORDERED.value,
            actual_amount=None,
        ),
        models.ExecutionModel(
            request_id=request_models[8].id,
            status=ExecutionStatus.DELIVERED.value,
            actual_amount=None,
        ),
        models.ExecutionModel(
            request_id=request_models[9].id,
            status=ExecutionStatus.INVOICED.value,
            actual_amount=Decimal("500000"),
        ),
        models.ExecutionModel(
            request_id=request_models[3].id,
            status=ExecutionStatus.PAID.value,
            actual_amount=Decimal("1100000"),
        ),
        models.ExecutionModel(
            request_id=request_models[5].id,
            status=ExecutionStatus.CANCELED.value,
            actual_amount=None,
        ),
    ]
    session.add_all(execution_models)

    tx_models: list[models.BudgetTransactionModel] = []
    commit_pairs = [
        (request_models[3], plan_models[3]),
        (request_models[7], plan_models[7]),
        (request_models[8], plan_models[8]),
        (request_models[9], plan_models[9]),
        (request_models[10], plan_models[10]),
        (request_models[6], plan_models[6]),
    ]
    for request, plan in commit_pairs:
        budget_id = budget_id_by_key[(plan.fiscal_year, plan.category_id)]
        tx_models.append(
            models.BudgetTransactionModel(
                budget_id=budget_id,
                request_id=request.id,
                tx_type=BudgetTxType.COMMIT.value,
                amount=request.requested_amount,
                reason="seed",
                created_by="system",
                created_at=datetime.utcnow(),
            )
        )

    actual_pairs = [
        (request_models[3], execution_models[4], plan_models[3]),
    ]
    for request, execution, plan in actual_pairs:
        budget_id = budget_id_by_key[(plan.fiscal_year, plan.category_id)]
        tx_models.append(
            models.BudgetTransactionModel(
                budget_id=budget_id,
                request_id=request.id,
                tx_type=BudgetTxType.ACTUALIZE.value,
                amount=execution.actual_amount or Decimal("0"),
                reason="seed",
                created_by="system",
                created_at=datetime.utcnow(),
            )
        )

    uncommit_request = request_models[5]
    uncommit_plan = plan_models[5]
    uncommit_budget_id = budget_id_by_key[(uncommit_plan.fiscal_year, uncommit_plan.category_id)]
    tx_models.append(
        models.BudgetTransactionModel(
            budget_id=uncommit_budget_id,
            request_id=uncommit_request.id,
            tx_type=BudgetTxType.UNCOMMIT.value,
            amount=uncommit_request.requested_amount,
            reason="seed",
            created_by="system",
            created_at=datetime.utcnow(),
        )
    )

    revert_request = request_models[3]
    revert_plan = plan_models[3]
    revert_budget_id = budget_id_by_key[(revert_plan.fiscal_year, revert_plan.category_id)]
    tx_models.append(
        models.BudgetTransactionModel(
            budget_id=revert_budget_id,
            request_id=revert_request.id,
            tx_type=BudgetTxType.REVERT_ACTUAL.value,
            amount=Decimal("100000"),
            reason="seed",
            created_by="system",
            created_at=datetime.utcnow(),
        )
    )

    tx_models.append(
        models.BudgetTransactionModel(
            budget_id=budget_models[0].id,
            request_id=None,
            tx_type=BudgetTxType.COMMIT.value,
            amount=Decimal("500000"),
            reason="seed",
            created_by="system",
            created_at=datetime.utcnow(),
        )
    )

    session.add_all(tx_models)

    audit_models = [
        models.AuditLogModel(
            actor="system",
            action="SEED_CREATED",
            target_type="Seed",
            target_id=None,
            reason="init",
            detail_json=json.dumps({"years": [2025, 2026]}, ensure_ascii=False),
            created_at=datetime.utcnow(),
        ),
        models.AuditLogModel(
            actor="system",
            action="PLAN_CREATED",
            target_type="Plan",
            target_id=plan_models[0].id,
            reason="seed",
            detail_json=json.dumps({"amount": str(plan_models[0].amount)}, ensure_ascii=False),
            created_at=datetime.utcnow(),
        ),
        models.AuditLogModel(
            actor="system",
            action="REQUEST_APPROVED",
            target_type="Request",
            target_id=request_models[1].id,
            reason="seed",
            detail_json=json.dumps({"requested_amount": str(request_models[1].requested_amount)}, ensure_ascii=False),
            created_at=datetime.utcnow(),
        ),
        models.AuditLogModel(
            actor="system",
            action="EXECUTION_PAID",
            target_type="Execution",
            target_id=execution_models[0].id,
            reason="seed",
            detail_json=json.dumps({"actual_amount": str(execution_models[0].actual_amount)}, ensure_ascii=False),
            created_at=datetime.utcnow(),
        ),
        models.AuditLogModel(
            actor="system",
            action="AUDIT_NOTE",
            target_type="Seed",
            target_id=None,
            reason=None,
            detail_json=json.dumps({"note": "optional_reason"}, ensure_ascii=False),
            created_at=datetime.utcnow(),
        ),
    ]
    session.add_all(audit_models)

    session.commit()
