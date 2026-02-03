from __future__ import annotations

from app.application.dto import (
    BudgetAdjustmentCreate,
    BudgetCreate,
    CategoryCreate,
    CategoryUpdate,
    ExecutionCreate,
    ExecutionPaid,
    PlanBulkCreate,
    PlanCreate,
    PlanUpdate,
    RequestCreate,
    SubcategoryCreate,
    SubcategoryUpdate,
)
from app.domain.entities import (
    AuditLog,
    Budget,
    BudgetAdjustment,
    Category,
    Execution,
    Plan,
    PlanChange,
    Request,
    Subcategory,
)
from app.domain.enums import ExecutionStatus, PlanStatus, RequestStatus
from app.domain.errors import BudgetOverrun
from app.domain.services import create_actualize_txs, create_commit_tx
from app.infrastructure.unit_of_work import UnitOfWork


def create_budget(uow: UnitOfWork, data: BudgetCreate) -> Budget:
    with uow:
        budget = Budget(
            id=None,
            fiscal_year=data.fiscal_year,
            department_id=data.department_id,
            category_id=data.category_id,
            initial_amount=data.initial_amount,
        )
        created = uow.budgets.add(budget)
        uow.audit_logs.add(
            AuditLog(
                id=None,
                actor="system",
                action="BUDGET_CREATED",
                target_type="Budget",
                target_id=created.id,
                reason=None,
                detail_json={"initial_amount": str(created.initial_amount)},
            )
        )
        return created


def adjust_budget(uow: UnitOfWork, budget_id: int, data: BudgetAdjustmentCreate) -> None:
    with uow:
        adjustment = BudgetAdjustment(
            amount=data.amount,
            reason=data.reason,
            created_by=data.created_by,
        )
        uow.budgets.add_adjustment(budget_id, adjustment)
        uow.audit_logs.add(
            AuditLog(
                id=None,
                actor=data.created_by,
                action="BUDGET_ADJUSTED",
                target_type="Budget",
                target_id=budget_id,
                reason=data.reason,
                detail_json={"amount": str(data.amount)},
            )
        )


def create_plan(uow: UnitOfWork, data: PlanCreate) -> Plan:
    with uow:
        plan = Plan(
            id=None,
            fiscal_year=data.fiscal_year,
            department_id=data.department_id,
            category_id=data.category_id,
            subcategory_id=data.subcategory_id,
            product_name=data.product_name,
            vendor=data.vendor,
            planned_month=data.planned_month,
            contract_type=data.contract_type,
            amount=data.amount,
            plan_type=data.plan_type,
            note=data.note,
        )
        created = uow.plans.add(plan)
        uow.audit_logs.add(
            AuditLog(
                id=None,
                actor="system",
                action="PLAN_CREATED",
                target_type="Plan",
                target_id=created.id,
                reason=None,
                detail_json={"amount": str(created.amount)},
            )
        )
        return created


def create_plans_bulk(uow: UnitOfWork, data: PlanBulkCreate) -> list[Plan]:
    created_plans: list[Plan] = []
    with uow:
        for plan_data in data.plans:
            plan = Plan(
                id=None,
                fiscal_year=plan_data.fiscal_year,
                department_id=plan_data.department_id,
                category_id=plan_data.category_id,
                subcategory_id=plan_data.subcategory_id,
                product_name=plan_data.product_name,
                vendor=plan_data.vendor,
                planned_month=plan_data.planned_month,
                contract_type=plan_data.contract_type,
                amount=plan_data.amount,
                plan_type=plan_data.plan_type,
                note=plan_data.note,
            )
            created = uow.plans.add(plan)
            uow.audit_logs.add(
                AuditLog(
                    id=None,
                    actor="system",
                    action="PLAN_CREATED",
                    target_type="Plan",
                    target_id=created.id,
                    reason="bulk_import",
                    detail_json={"amount": str(created.amount)},
                )
            )
            created_plans.append(created)
    return created_plans


def update_plan(uow: UnitOfWork, plan_id: int, data: PlanUpdate) -> Plan | None:
    with uow:
        current = uow.plans.get(plan_id)
        if not current:
            return None
        diff = {
            "before": {
                "category_id": current.category_id,
                "subcategory_id": current.subcategory_id,
                "product_name": current.product_name,
                "vendor": current.vendor,
                "planned_month": current.planned_month,
                "contract_type": current.contract_type,
                "amount": str(current.amount),
                "plan_type": current.plan_type,
                "note": current.note,
                "status": current.status.value,
            },
            "after": {
                "category_id": data.category_id,
                "subcategory_id": data.subcategory_id,
                "product_name": data.product_name,
                "vendor": data.vendor,
                "planned_month": data.planned_month,
                "contract_type": data.contract_type,
                "amount": str(data.amount),
                "plan_type": data.plan_type,
                "note": data.note,
                "status": data.status.value,
            },
        }
        current.category_id = data.category_id
        current.subcategory_id = data.subcategory_id
        current.product_name = data.product_name
        current.vendor = data.vendor
        current.planned_month = data.planned_month
        current.contract_type = data.contract_type
        current.amount = data.amount
        current.plan_type = data.plan_type
        current.note = data.note
        current.status = data.status
        uow.plans.update(current)
        change = PlanChange(
            id=None,
            plan_id=plan_id,
            changed_by=data.changed_by,
            reason=data.reason,
            diff_json=diff,
        )
        uow.plans.add_change(change)
        uow.audit_logs.add(
            AuditLog(
                id=None,
                actor=data.changed_by,
                action="PLAN_UPDATED",
                target_type="Plan",
                target_id=plan_id,
                reason=data.reason,
                detail_json=diff,
            )
        )
        return current


def list_plan_changes(uow: UnitOfWork, plan_id: int):
    with uow:
        return uow.plans.list_changes(plan_id)


def list_plans(
    uow: UnitOfWork,
    fiscal_year: int | None = None,
    department_id: int | None = None,
    category_id: int | None = None,
    subcategory_id: int | None = None,
    planned_month: str | None = None,
    plan_type: str | None = None,
    status: PlanStatus | None = None,
):
    with uow:
        return uow.plans.list(
            fiscal_year=fiscal_year,
            department_id=department_id,
            category_id=category_id,
            subcategory_id=subcategory_id,
            planned_month=planned_month,
            plan_type=plan_type,
            status=status,
        )


def get_plan(uow: UnitOfWork, plan_id: int) -> Plan | None:
    with uow:
        return uow.plans.get(plan_id)


def dashboard_summary(uow: UnitOfWork, fiscal_year: int, department_id: int):
    with uow:
        budget_total = uow.budgets.total_limit(fiscal_year=fiscal_year, department_id=department_id)
        plan_total = uow.plans.total_amount(fiscal_year=fiscal_year, department_id=department_id)
        return {"budget_total": budget_total, "plan_total": plan_total}


def create_request(uow: UnitOfWork, data: RequestCreate) -> Request:
    with uow:
        request = Request(id=None, plan_id=data.plan_id, requested_amount=data.requested_amount)
        created = uow.requests.add(request)
        uow.audit_logs.add(
            AuditLog(
                id=None,
                actor=data.created_by,
                action="REQUEST_CREATED",
                target_type="Request",
                target_id=created.id,
                reason=data.reason,
                detail_json={"requested_amount": str(created.requested_amount), "plan_id": created.plan_id},
            )
        )
        return created


def submit_request(uow: UnitOfWork, request_id: int) -> Request | None:
    with uow:
        request = uow.requests.get(request_id)
        if not request:
            return None
        request.submit()
        uow.requests.update(request)
        uow.audit_logs.add(
            AuditLog(
                id=None,
                actor="system",
                action="REQUEST_SUBMITTED",
                target_type="Request",
                target_id=request.id,
                reason=None,
                detail_json={},
            )
        )
        return request


def approvals_inbox(uow: UnitOfWork) -> list[Request]:
    with uow:
        return uow.requests.list_by_status(RequestStatus.SUBMITTED)


def list_requests(uow: UnitOfWork, status: RequestStatus | None = None) -> list[Request]:
    with uow:
        return uow.requests.list(status=status)


def get_request(uow: UnitOfWork, request_id: int) -> Request | None:
    with uow:
        return uow.requests.get(request_id)


def approve_request(uow: UnitOfWork, request_id: int, reason: str, approved_by: str) -> Request | None:
    with uow:
        request = uow.requests.get(request_id)
        if not request:
            return None
        request.approve()
        uow.requests.update(request)
        uow.audit_logs.add(
            AuditLog(
                id=None,
                actor=approved_by,
                action="REQUEST_APPROVED",
                target_type="Request",
                target_id=request.id,
                reason=reason,
                detail_json={},
            )
        )

        if request.plan_id is None:
            return request

        plan = uow.plans.get(request.plan_id)
        if not plan:
            return request

        budget = uow.budgets.get_by_keys(plan.fiscal_year, plan.department_id, plan.category_id)
        if not budget:
            return request

        totals = uow.transactions.totals_for_budget(budget.id)
        remaining = budget.remaining(commit_total=totals["commit"], actual_total=totals["actual"])
        if remaining < request.requested_amount:
            raise BudgetOverrun("Remaining budget is insufficient")

        tx = create_commit_tx(budget_id=budget.id, request=request, reason=reason, created_by=approved_by)
        uow.transactions.add_many([tx])
        return request


def return_request(uow: UnitOfWork, request_id: int) -> Request | None:
    with uow:
        request = uow.requests.get(request_id)
        if not request:
            return None
        request.return_request()
        uow.requests.update(request)
        uow.audit_logs.add(
            AuditLog(
                id=None,
                actor="system",
                action="REQUEST_RETURNED",
                target_type="Request",
                target_id=request.id,
                reason=None,
                detail_json={},
            )
        )
        return request


def reject_request(uow: UnitOfWork, request_id: int) -> Request | None:
    with uow:
        request = uow.requests.get(request_id)
        if not request:
            return None
        request.reject()
        uow.requests.update(request)
        uow.audit_logs.add(
            AuditLog(
                id=None,
                actor="system",
                action="REQUEST_REJECTED",
                target_type="Request",
                target_id=request.id,
                reason=None,
                detail_json={},
            )
        )
        return request


def create_execution(uow: UnitOfWork, data: ExecutionCreate) -> Execution:
    with uow:
        execution = Execution(id=None, request_id=data.request_id)
        created = uow.executions.add(execution)
        uow.audit_logs.add(
            AuditLog(
                id=None,
                actor="system",
                action="EXECUTION_CREATED",
                target_type="Execution",
                target_id=created.id,
                reason=None,
                detail_json={"request_id": created.request_id},
            )
        )
        return created


def list_executions(uow: UnitOfWork, status: ExecutionStatus | None = None) -> list[Execution]:
    with uow:
        return uow.executions.list(status=status)


def set_execution_status(uow: UnitOfWork, execution_id: int, status: ExecutionStatus) -> Execution | None:
    with uow:
        execution = uow.executions.get(execution_id)
        if not execution:
            return None
        execution.set_status(status)
        uow.executions.update(execution)
        uow.audit_logs.add(
            AuditLog(
                id=None,
                actor="system",
                action="EXECUTION_STATUS_UPDATED",
                target_type="Execution",
                target_id=execution.id,
                reason=None,
                detail_json={"status": execution.status.value},
            )
        )
        return execution


def mark_execution_paid(uow: UnitOfWork, execution_id: int, data: ExecutionPaid) -> Execution | None:
    with uow:
        execution = uow.executions.get(execution_id)
        if not execution:
            return None
        request = uow.requests.get(execution.request_id)
        if not request:
            return None

        execution.mark_paid(
            actual_amount=data.actual_amount,
            requested_amount=request.requested_amount,
            allow_over=data.allow_over,
        )
        uow.executions.update(execution)
        uow.audit_logs.add(
            AuditLog(
                id=None,
                actor=data.paid_by,
                action="EXECUTION_PAID",
                target_type="Execution",
                target_id=execution.id,
                reason=data.reason,
                detail_json={"actual_amount": str(data.actual_amount)},
            )
        )

        if request.plan_id is None:
            return execution

        plan = uow.plans.get(request.plan_id)
        if not plan:
            return execution

        budget = uow.budgets.get_by_keys(plan.fiscal_year, plan.department_id, plan.category_id)
        if not budget:
            return execution

        txs = create_actualize_txs(
            budget_id=budget.id,
            request_id=request.id,
            requested_amount=request.requested_amount,
            actual_amount=data.actual_amount,
            reason=data.reason,
            created_by=data.paid_by,
        )
        uow.transactions.add_many(txs)
        return execution


def report_budget_summary(uow: UnitOfWork, fiscal_year: int, department_id: int):
    with uow:
        budgets = uow.budgets.list(fiscal_year=fiscal_year, department_id=department_id)
        summaries = []
        for budget in budgets:
            totals = uow.transactions.totals_for_budget(budget.id)
            remaining = budget.remaining(commit_total=totals["commit"], actual_total=totals["actual"])
            summaries.append(
                {
                    "category_id": budget.category_id,
                    "budget_total": budget.total_limit(),
                    "commit_total": totals["commit"],
                    "actual_total": totals["actual"],
                    "remaining": remaining,
                }
            )
        return summaries


def report_monthly_summary(uow: UnitOfWork, fiscal_year: int, department_id: int):
    with uow:
        plan_totals = uow.plans.monthly_totals(fiscal_year=fiscal_year, department_id=department_id)
        actual_totals = uow.executions.monthly_actual_totals(fiscal_year=fiscal_year, department_id=department_id)
        months = sorted(set(plan_totals.keys()) | set(actual_totals.keys()))
        return [
            {
                "month": month,
                "plan_total": plan_totals.get(month, 0),
                "actual_total": actual_totals.get(month, 0),
            }
            for month in months
        ]


def report_unplanned_requests(uow: UnitOfWork):
    with uow:
        return uow.requests.unplanned_summary()


def list_audit_logs(
    uow: UnitOfWork,
    actor: str | None = None,
    action: str | None = None,
    target_type: str | None = None,
    target_id: int | None = None,
):
    with uow:
        return uow.audit_logs.list(actor=actor, action=action, target_type=target_type, target_id=target_id)


def recent_audit_logs(uow: UnitOfWork, limit: int = 10):
    with uow:
        logs = uow.audit_logs.list()
        return logs[:limit]


def create_category(uow: UnitOfWork, data: CategoryCreate) -> Category:
    with uow:
        category = Category(id=None, name=data.name)
        return uow.categories.add(category)


def list_categories(uow: UnitOfWork) -> list[Category]:
    with uow:
        return uow.categories.list()


def update_category(uow: UnitOfWork, category_id: int, data: CategoryUpdate) -> bool:
    with uow:
        return uow.categories.update(category_id, data.name)


def delete_category(uow: UnitOfWork, category_id: int) -> bool:
    with uow:
        return uow.categories.delete(category_id)


def create_subcategory(uow: UnitOfWork, data: SubcategoryCreate) -> Subcategory:
    with uow:
        subcategory = Subcategory(id=None, category_id=data.category_id, name=data.name)
        return uow.subcategories.add(subcategory)


def list_subcategories(uow: UnitOfWork, category_id: int | None = None) -> list[Subcategory]:
    with uow:
        return uow.subcategories.list(category_id=category_id)


def update_subcategory(uow: UnitOfWork, subcategory_id: int, data: SubcategoryUpdate) -> bool:
    with uow:
        return uow.subcategories.update(subcategory_id, data.category_id, data.name)


def delete_subcategory(uow: UnitOfWork, subcategory_id: int) -> bool:
    with uow:
        return uow.subcategories.delete(subcategory_id)
