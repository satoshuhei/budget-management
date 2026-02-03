from __future__ import annotations

import json
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.entities import (
    AuditLog,
    Budget,
    BudgetAdjustment,
    BudgetTransaction,
    Category,
    Execution,
    Plan,
    PlanChange,
    Request,
    Subcategory,
)
from app.domain.enums import BudgetTxType, ExecutionStatus, PlanStatus, RequestStatus
from app.infrastructure import models


class BudgetRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, budget: Budget) -> Budget:
        model = models.BudgetModel(
            fiscal_year=budget.fiscal_year,
            department_id=budget.department_id,
            category_id=budget.category_id,
            initial_amount=budget.initial_amount,
        )
        self.session.add(model)
        self.session.flush()
        budget.id = model.id
        return budget

    def get(self, budget_id: int) -> Budget | None:
        model = self.session.get(models.BudgetModel, budget_id)
        if not model:
            return None
        adjustments = [
            BudgetAdjustment(
                amount=adj.amount,
                reason=adj.reason,
                created_by=adj.created_by,
                created_at=adj.created_at,
            )
            for adj in model.adjustments
        ]
        return Budget(
            id=model.id,
            fiscal_year=model.fiscal_year,
            department_id=model.department_id,
            category_id=model.category_id,
            initial_amount=model.initial_amount,
            adjustments=adjustments,
        )

    def get_by_keys(self, fiscal_year: int, department_id: int, category_id: int) -> Budget | None:
        model = (
            self.session.execute(
                select(models.BudgetModel)
                .where(models.BudgetModel.fiscal_year == fiscal_year)
                .where(models.BudgetModel.department_id == department_id)
                .where(models.BudgetModel.category_id == category_id)
            )
            .scalars()
            .first()
        )
        if not model:
            return None
        adjustments = [
            BudgetAdjustment(
                amount=adj.amount,
                reason=adj.reason,
                created_by=adj.created_by,
                created_at=adj.created_at,
            )
            for adj in model.adjustments
        ]
        return Budget(
            id=model.id,
            fiscal_year=model.fiscal_year,
            department_id=model.department_id,
            category_id=model.category_id,
            initial_amount=model.initial_amount,
            adjustments=adjustments,
        )

    def list(self, fiscal_year: int | None = None, department_id: int | None = None) -> list[Budget]:
        query = select(models.BudgetModel)
        if fiscal_year is not None:
            query = query.where(models.BudgetModel.fiscal_year == fiscal_year)
        if department_id is not None:
            query = query.where(models.BudgetModel.department_id == department_id)
        results = self.session.execute(query).scalars().all()
        budgets: list[Budget] = []
        for model in results:
            adjustments = [
                BudgetAdjustment(
                    amount=adj.amount,
                    reason=adj.reason,
                    created_by=adj.created_by,
                    created_at=adj.created_at,
                )
                for adj in model.adjustments
            ]
            budgets.append(
                Budget(
                    id=model.id,
                    fiscal_year=model.fiscal_year,
                    department_id=model.department_id,
                    category_id=model.category_id,
                    initial_amount=model.initial_amount,
                    adjustments=adjustments,
                )
            )
        return budgets

    def add_adjustment(self, budget_id: int, adjustment: BudgetAdjustment) -> None:
        model = models.BudgetAdjustmentModel(
            budget_id=budget_id,
            amount=adjustment.amount,
            reason=adjustment.reason,
            created_by=adjustment.created_by,
            created_at=adjustment.created_at,
        )
        self.session.add(model)

    def total_limit(self, fiscal_year: int | None = None, department_id: int | None = None) -> Decimal:
        filters = []
        if fiscal_year is not None:
            filters.append(models.BudgetModel.fiscal_year == fiscal_year)
        if department_id is not None:
            filters.append(models.BudgetModel.department_id == department_id)

        initial_total = (
            self.session.execute(select(func.coalesce(func.sum(models.BudgetModel.initial_amount), 0)).where(*filters))
            .scalar_one()
        )
        adjustment_total = (
            self.session.execute(
                select(func.coalesce(func.sum(models.BudgetAdjustmentModel.amount), 0)).join(
                    models.BudgetModel,
                    models.BudgetAdjustmentModel.budget_id == models.BudgetModel.id,
                )
                .where(*filters)
            )
            .scalar_one()
        )
        return Decimal(initial_total) + Decimal(adjustment_total)


class PlanRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, plan: Plan) -> Plan:
        model = models.PlanModel(
            fiscal_year=plan.fiscal_year,
            department_id=plan.department_id,
            category_id=plan.category_id,
            subcategory_id=plan.subcategory_id,
            product_name=plan.product_name,
            vendor=plan.vendor,
            planned_month=plan.planned_month,
            contract_type=plan.contract_type,
            amount=plan.amount,
            plan_type=plan.plan_type,
            note=plan.note,
            status=plan.status.value,
        )
        self.session.add(model)
        self.session.flush()
        plan.id = model.id
        return plan

    def get(self, plan_id: int) -> Plan | None:
        model = self.session.get(models.PlanModel, plan_id)
        if not model:
            return None
        return Plan(
            id=model.id,
            fiscal_year=model.fiscal_year,
            department_id=model.department_id,
            category_id=model.category_id,
            subcategory_id=model.subcategory_id,
            product_name=model.product_name,
            vendor=model.vendor,
            planned_month=model.planned_month,
            contract_type=model.contract_type,
            amount=model.amount,
            plan_type=model.plan_type,
            note=model.note,
            status=PlanStatus(model.status),
        )

    def list(
        self,
        fiscal_year: int | None = None,
        department_id: int | None = None,
        category_id: int | None = None,
        subcategory_id: int | None = None,
        planned_month: str | None = None,
        plan_type: str | None = None,
        status: PlanStatus | None = None,
    ) -> list[Plan]:
        query = select(models.PlanModel)
        if fiscal_year is not None:
            query = query.where(models.PlanModel.fiscal_year == fiscal_year)
        if department_id is not None:
            query = query.where(models.PlanModel.department_id == department_id)
        if category_id is not None:
            query = query.where(models.PlanModel.category_id == category_id)
        if subcategory_id is not None:
            query = query.where(models.PlanModel.subcategory_id == subcategory_id)
        if planned_month is not None:
            query = query.where(models.PlanModel.planned_month == planned_month)
        if plan_type is not None:
            query = query.where(models.PlanModel.plan_type == plan_type)
        if status is not None:
            query = query.where(models.PlanModel.status == status.value)
        results = self.session.execute(query).scalars().all()
        return [
            Plan(
                id=m.id,
                fiscal_year=m.fiscal_year,
                department_id=m.department_id,
                category_id=m.category_id,
                subcategory_id=m.subcategory_id,
                product_name=m.product_name,
                vendor=m.vendor,
                planned_month=m.planned_month,
                contract_type=m.contract_type,
                amount=m.amount,
                plan_type=m.plan_type,
                note=m.note,
                status=PlanStatus(m.status),
            )
            for m in results
        ]

    def total_amount(
        self,
        fiscal_year: int | None = None,
        department_id: int | None = None,
        category_id: int | None = None,
        subcategory_id: int | None = None,
    ) -> Decimal:
        query = select(func.coalesce(func.sum(models.PlanModel.amount), 0))
        if fiscal_year is not None:
            query = query.where(models.PlanModel.fiscal_year == fiscal_year)
        if department_id is not None:
            query = query.where(models.PlanModel.department_id == department_id)
        if category_id is not None:
            query = query.where(models.PlanModel.category_id == category_id)
        if subcategory_id is not None:
            query = query.where(models.PlanModel.subcategory_id == subcategory_id)
        return Decimal(self.session.execute(query).scalar_one())

    def monthly_totals(self, fiscal_year: int, department_id: int) -> dict[str, Decimal]:
        rows = (
            self.session.execute(
                select(models.PlanModel.planned_month, func.coalesce(func.sum(models.PlanModel.amount), 0))
                .where(models.PlanModel.fiscal_year == fiscal_year)
                .where(models.PlanModel.department_id == department_id)
                .group_by(models.PlanModel.planned_month)
            )
            .all()
        )
        return {month: Decimal(total) for month, total in rows}

    def update(self, plan: Plan) -> None:
        model = self.session.get(models.PlanModel, plan.id)
        if not model:
            return
        model.category_id = plan.category_id
        model.subcategory_id = plan.subcategory_id
        model.product_name = plan.product_name
        model.vendor = plan.vendor
        model.planned_month = plan.planned_month
        model.contract_type = plan.contract_type
        model.amount = plan.amount
        model.plan_type = plan.plan_type
        model.note = plan.note
        model.status = plan.status.value

    def add_change(self, change: PlanChange) -> None:
        model = models.PlanChangeModel(
            plan_id=change.plan_id,
            changed_by=change.changed_by,
            reason=change.reason,
            diff_json=json.dumps(change.diff_json, ensure_ascii=False),
            changed_at=change.changed_at,
        )
        self.session.add(model)

    def list_changes(self, plan_id: int) -> list[PlanChange]:
        results = (
            self.session.execute(select(models.PlanChangeModel).where(models.PlanChangeModel.plan_id == plan_id))
            .scalars()
            .all()
        )
        return [
            PlanChange(
                id=m.id,
                plan_id=m.plan_id,
                changed_by=m.changed_by,
                reason=m.reason,
                diff_json=json.loads(m.diff_json),
                changed_at=m.changed_at,
            )
            for m in results
        ]


class RequestRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, request: Request) -> Request:
        model = models.RequestModel(
            plan_id=request.plan_id,
            requested_amount=request.requested_amount,
            status=request.status.value,
        )
        self.session.add(model)
        self.session.flush()
        request.id = model.id
        return request

    def get(self, request_id: int) -> Request | None:
        model = self.session.get(models.RequestModel, request_id)
        if not model:
            return None
        return Request(
            id=model.id,
            plan_id=model.plan_id,
            requested_amount=Decimal(model.requested_amount),
            status=RequestStatus(model.status),
        )

    def update(self, request: Request) -> None:
        model = self.session.get(models.RequestModel, request.id)
        if not model:
            return
        model.status = request.status.value

    def list_by_status(self, status: RequestStatus) -> list[Request]:
        results = (
            self.session.execute(select(models.RequestModel).where(models.RequestModel.status == status.value))
            .scalars()
            .all()
        )
        return [
            Request(
                id=m.id,
                plan_id=m.plan_id,
                requested_amount=Decimal(m.requested_amount),
                status=RequestStatus(m.status),
            )
            for m in results
        ]

    def list(self, status: RequestStatus | None = None) -> list[Request]:
        query = select(models.RequestModel)
        if status is not None:
            query = query.where(models.RequestModel.status == status.value)
        results = self.session.execute(query).scalars().all()
        return [
            Request(
                id=m.id,
                plan_id=m.plan_id,
                requested_amount=Decimal(m.requested_amount),
                status=RequestStatus(m.status),
            )
            for m in results
        ]

    def unplanned_summary(self) -> dict[str, Decimal | int]:
        row = (
            self.session.execute(
                select(
                    func.count(models.RequestModel.id),
                    func.coalesce(func.sum(models.RequestModel.requested_amount), 0),
                ).where(models.RequestModel.plan_id.is_(None))
            )
            .one()
        )
        return {"count": int(row[0]), "total_amount": Decimal(row[1])}


class ExecutionRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, execution: Execution) -> Execution:
        model = models.ExecutionModel(
            request_id=execution.request_id,
            status=execution.status.value,
            actual_amount=execution.actual_amount,
        )
        self.session.add(model)
        self.session.flush()
        execution.id = model.id
        return execution

    def get(self, execution_id: int) -> Execution | None:
        model = self.session.get(models.ExecutionModel, execution_id)
        if not model:
            return None
        return Execution(
            id=model.id,
            request_id=model.request_id,
            status=ExecutionStatus(model.status),
            actual_amount=model.actual_amount,
        )

    def update(self, execution: Execution) -> None:
        model = self.session.get(models.ExecutionModel, execution.id)
        if not model:
            return
        model.status = execution.status.value
        model.actual_amount = execution.actual_amount

    def list(self, status: ExecutionStatus | None = None) -> list[Execution]:
        query = select(models.ExecutionModel)
        if status is not None:
            query = query.where(models.ExecutionModel.status == status.value)
        results = self.session.execute(query).scalars().all()
        return [
            Execution(
                id=m.id,
                request_id=m.request_id,
                status=ExecutionStatus(m.status),
                actual_amount=m.actual_amount,
            )
            for m in results
        ]

    def monthly_actual_totals(self, fiscal_year: int, department_id: int) -> dict[str, Decimal]:
        rows = (
            self.session.execute(
                select(
                    models.PlanModel.planned_month,
                    func.coalesce(func.sum(models.ExecutionModel.actual_amount), 0),
                )
                .join(models.RequestModel, models.ExecutionModel.request_id == models.RequestModel.id)
                .join(models.PlanModel, models.RequestModel.plan_id == models.PlanModel.id)
                .where(models.PlanModel.fiscal_year == fiscal_year)
                .where(models.PlanModel.department_id == department_id)
                .where(models.ExecutionModel.status == ExecutionStatus.PAID.value)
                .group_by(models.PlanModel.planned_month)
            )
            .all()
        )
        return {month: Decimal(total) for month, total in rows}


class BudgetTransactionRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_many(self, txs: list[BudgetTransaction]) -> None:
        for tx in txs:
            self.session.add(
                models.BudgetTransactionModel(
                    budget_id=tx.budget_id,
                    request_id=tx.request_id,
                    tx_type=tx.tx_type.value,
                    amount=tx.amount,
                    reason=tx.reason,
                    created_by=tx.created_by,
                    created_at=tx.created_at,
                )
            )

    def totals_for_budget(self, budget_id: int) -> dict[str, Decimal]:
        rows = (
            self.session.execute(
                select(models.BudgetTransactionModel.tx_type, models.BudgetTransactionModel.amount).where(
                    models.BudgetTransactionModel.budget_id == budget_id
                )
            )
            .all()
        )
        commit = Decimal("0")
        actual = Decimal("0")
        for tx_type, amount in rows:
            if tx_type == BudgetTxType.COMMIT.value:
                commit += Decimal(amount)
            if tx_type == BudgetTxType.UNCOMMIT.value:
                commit -= Decimal(amount)
            if tx_type == BudgetTxType.ACTUALIZE.value:
                actual += Decimal(amount)
            if tx_type == BudgetTxType.REVERT_ACTUAL.value:
                actual -= Decimal(amount)
        return {"commit": commit, "actual": actual}


class AuditLogRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, log: AuditLog) -> AuditLog:
        model = models.AuditLogModel(
            actor=log.actor,
            action=log.action,
            target_type=log.target_type,
            target_id=log.target_id,
            reason=log.reason,
            detail_json=json.dumps(log.detail_json, ensure_ascii=False),
            created_at=log.created_at,
        )
        self.session.add(model)
        self.session.flush()
        log.id = model.id
        return log

    def list(
        self,
        actor: str | None = None,
        action: str | None = None,
        target_type: str | None = None,
        target_id: int | None = None,
    ) -> list[AuditLog]:
        query = select(models.AuditLogModel)
        if actor is not None:
            query = query.where(models.AuditLogModel.actor == actor)
        if action is not None:
            query = query.where(models.AuditLogModel.action == action)
        if target_type is not None:
            query = query.where(models.AuditLogModel.target_type == target_type)
        if target_id is not None:
            query = query.where(models.AuditLogModel.target_id == target_id)
        results = self.session.execute(query.order_by(models.AuditLogModel.created_at.desc())).scalars().all()
        return [
            AuditLog(
                id=m.id,
                actor=m.actor,
                action=m.action,
                target_type=m.target_type,
                target_id=m.target_id,
                reason=m.reason,
                detail_json=json.loads(m.detail_json),
                created_at=m.created_at,
            )
            for m in results
        ]


class CategoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, category: Category) -> Category:
        model = models.CategoryModel(name=category.name)
        self.session.add(model)
        self.session.flush()
        category.id = model.id
        return category

    def list(self) -> list[Category]:
        results = self.session.execute(select(models.CategoryModel)).scalars().all()
        return [Category(id=m.id, name=m.name) for m in results]

    def update(self, category_id: int, name: str) -> bool:
        model = self.session.get(models.CategoryModel, category_id)
        if not model:
            return False
        model.name = name
        return True

    def delete(self, category_id: int) -> bool:
        model = self.session.get(models.CategoryModel, category_id)
        if not model:
            return False
        self.session.delete(model)
        return True


class SubcategoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, subcategory: Subcategory) -> Subcategory:
        model = models.SubcategoryModel(category_id=subcategory.category_id, name=subcategory.name)
        self.session.add(model)
        self.session.flush()
        subcategory.id = model.id
        return subcategory

    def list(self, category_id: int | None = None) -> list[Subcategory]:
        query = select(models.SubcategoryModel)
        if category_id is not None:
            query = query.where(models.SubcategoryModel.category_id == category_id)
        results = self.session.execute(query).scalars().all()
        return [Subcategory(id=m.id, category_id=m.category_id, name=m.name) for m in results]

    def update(self, subcategory_id: int, category_id: int, name: str) -> bool:
        model = self.session.get(models.SubcategoryModel, subcategory_id)
        if not model:
            return False
        model.category_id = category_id
        model.name = name
        return True

    def delete(self, subcategory_id: int) -> bool:
        model = self.session.get(models.SubcategoryModel, subcategory_id)
        if not model:
            return False
        self.session.delete(model)
        return True
