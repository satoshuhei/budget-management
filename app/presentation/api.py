from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

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
from app.application.usecases import (
    adjust_budget,
    approve_request,
    approvals_inbox,
    create_execution,
    create_budget,
    create_category,
    create_plan,
    create_plans_bulk,
    create_request,
    dashboard_summary,
    list_categories,
    list_plan_changes,
    list_plans,
    get_plan,
    list_requests,
    list_audit_logs,
    mark_execution_paid,
    reject_request,
    report_budget_summary,
    report_monthly_summary,
    report_unplanned_requests,
    return_request,
    list_executions,
    set_execution_status,
    submit_request,
    update_plan,
    get_request,
    recent_audit_logs,
    create_subcategory,
    list_subcategories,
    update_category,
    delete_category,
    update_subcategory,
    delete_subcategory,
)
from app.domain.enums import ExecutionStatus, PlanStatus, RequestStatus, Role
from app.domain.errors import BudgetOverrun
from app.presentation.auth import CurrentUser, get_current_user, require_roles
from app.presentation.auth_store import authenticate
from app.infrastructure.unit_of_work import UnitOfWork
from app.infrastructure.client_log_store import append_client_log

router = APIRouter(prefix="/api")


class BudgetResponse(BaseModel):
    id: int
    fiscal_year: int
    department_id: int
    category_id: int
    initial_amount: Decimal


class PlanResponse(BaseModel):
    id: int
    fiscal_year: int
    department_id: int
    category_id: int
    subcategory_id: int
    product_name: str
    vendor: str
    planned_month: str
    contract_type: str
    amount: Decimal
    plan_type: str
    note: str
    status: str


class RequestResponse(BaseModel):
    id: int
    plan_id: int | None
    requested_amount: Decimal
    status: str


class ExecutionResponse(BaseModel):
    id: int
    request_id: int
    status: str
    actual_amount: Decimal | None


class DashboardSummaryResponse(BaseModel):
    budget_total: Decimal
    plan_total: Decimal


class BudgetSummaryRow(BaseModel):
    category_id: int
    budget_total: Decimal
    commit_total: Decimal
    actual_total: Decimal
    remaining: Decimal


class MonthlySummaryRow(BaseModel):
    month: str
    plan_total: Decimal
    actual_total: Decimal


class UnplannedRequestSummary(BaseModel):
    count: int
    total_amount: Decimal


class AuditLogResponse(BaseModel):
    id: int
    actor: str
    action: str
    target_type: str
    target_id: int | None
    reason: str | None
    detail_json: dict
    created_at: str


class CategoryResponse(BaseModel):
    id: int
    name: str


class SubcategoryResponse(BaseModel):
    id: int
    category_id: int
    name: str


class ClientLogRequest(BaseModel):
    message: str
    stack: str | None = None
    context: str | None = None
    info: dict | None = None
    createdAt: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    username: str
    role: str
    message: str


@router.post("/budgets", response_model=BudgetResponse)
def post_budget(payload: BudgetCreate, _user: CurrentUser = Depends(require_roles(Role.BUDGET_ADMIN))):
    budget = create_budget(UnitOfWork(), payload)
    return BudgetResponse(
        id=budget.id,
        fiscal_year=budget.fiscal_year,
        department_id=budget.department_id,
        category_id=budget.category_id,
        initial_amount=budget.initial_amount,
    )


@router.post("/auth/login", response_model=LoginResponse)
def post_login(payload: LoginRequest):
    role = authenticate(payload.username, payload.password)
    if not role:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return LoginResponse(
        username=payload.username,
        role=role.value,
        message="Use X-User and X-Role headers in subsequent requests",
    )


@router.post("/client-logs")
def post_client_log(payload: ClientLogRequest):
    append_client_log(payload.model_dump())
    return {"status": "ok"}


@router.get("/auth/me", response_model=LoginResponse)
def get_login_profile(user: CurrentUser = Depends(get_current_user)):
    return LoginResponse(username=user.username, role=user.role.value, message="ok")


@router.post("/budgets/{budget_id}/adjustments")
def post_budget_adjustment(
    budget_id: int, payload: BudgetAdjustmentCreate, _user: CurrentUser = Depends(require_roles(Role.BUDGET_ADMIN))
):
    adjust_budget(UnitOfWork(), budget_id, payload)
    return {"status": "ok"}


@router.post("/plans", response_model=PlanResponse)
def post_plan(payload: PlanCreate, _user: CurrentUser = Depends(require_roles(Role.USER, Role.BUDGET_ADMIN))):
    plan = create_plan(UnitOfWork(), payload)
    return PlanResponse(
        id=plan.id,
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


@router.post("/plans/bulk", response_model=list[PlanResponse])
def post_plans_bulk(
    payload: PlanBulkCreate, _user: CurrentUser = Depends(require_roles(Role.USER, Role.BUDGET_ADMIN))
):
    plans = create_plans_bulk(UnitOfWork(), payload)
    return [
        PlanResponse(
            id=plan.id,
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
        for plan in plans
    ]


@router.put("/plans/{plan_id}", response_model=PlanResponse)
def put_plan(plan_id: int, payload: PlanUpdate, _user: CurrentUser = Depends(require_roles(Role.USER, Role.BUDGET_ADMIN))):
    plan = update_plan(UnitOfWork(), plan_id, payload)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return PlanResponse(
        id=plan.id,
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


@router.get("/plans/{plan_id}/changes")
def get_plan_changes(plan_id: int, _user: CurrentUser = Depends(require_roles(Role.USER, Role.BUDGET_ADMIN))):
    changes = list_plan_changes(UnitOfWork(), plan_id)
    return [
        {
            "id": c.id,
            "plan_id": c.plan_id,
            "changed_by": c.changed_by,
            "reason": c.reason,
            "diff": c.diff_json,
            "changed_at": c.changed_at.isoformat(),
        }
        for c in changes
    ]


@router.get("/plans/{plan_id}", response_model=PlanResponse)
def get_plan_detail(plan_id: int, _user: CurrentUser = Depends(require_roles(Role.USER, Role.BUDGET_ADMIN))):
    plan = get_plan(UnitOfWork(), plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return PlanResponse(
        id=plan.id,
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


@router.get("/plans", response_model=list[PlanResponse])
def get_plans(
    fiscal_year: int | None = None,
    department_id: int | None = None,
    category_id: int | None = None,
    subcategory_id: int | None = None,
    planned_month: str | None = None,
    plan_type: str | None = None,
    status: PlanStatus | None = None,
    _user: CurrentUser = Depends(require_roles(Role.USER, Role.BUDGET_ADMIN)),
):
    plans = list_plans(
        UnitOfWork(),
        fiscal_year=fiscal_year,
        department_id=department_id,
        category_id=category_id,
        subcategory_id=subcategory_id,
        planned_month=planned_month,
        plan_type=plan_type,
        status=status,
    )
    return [
        PlanResponse(
            id=plan.id,
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
        for plan in plans
    ]


@router.post("/requests", response_model=RequestResponse)
def post_request(payload: RequestCreate, _user: CurrentUser = Depends(require_roles(Role.USER, Role.BUDGET_ADMIN))):
    request = create_request(UnitOfWork(), payload)
    return RequestResponse(
        id=request.id,
        plan_id=request.plan_id,
        requested_amount=request.requested_amount,
        status=request.status.value,
    )


@router.get("/requests", response_model=list[RequestResponse])
def get_requests(
    status: RequestStatus | None = None,
    _user: CurrentUser = Depends(require_roles(Role.USER, Role.BUDGET_ADMIN)),
):
    requests = list_requests(UnitOfWork(), status=status)
    return [
        RequestResponse(
            id=req.id,
            plan_id=req.plan_id,
            requested_amount=req.requested_amount,
            status=req.status.value,
        )
        for req in requests
    ]


@router.get("/requests/{request_id}", response_model=RequestResponse)
def get_request_detail(
    request_id: int,
    _user: CurrentUser = Depends(require_roles(Role.USER, Role.BUDGET_ADMIN)),
):
    request = get_request(UnitOfWork(), request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return RequestResponse(
        id=request.id,
        plan_id=request.plan_id,
        requested_amount=request.requested_amount,
        status=request.status.value,
    )


@router.post("/requests/{request_id}/submit", response_model=RequestResponse)
def post_request_submit(request_id: int, _user: CurrentUser = Depends(require_roles(Role.USER, Role.BUDGET_ADMIN))):
    request = submit_request(UnitOfWork(), request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return RequestResponse(
        id=request.id,
        plan_id=request.plan_id,
        requested_amount=request.requested_amount,
        status=request.status.value,
    )


@router.get("/approvals/inbox", response_model=list[RequestResponse])
def get_approvals_inbox(_user: CurrentUser = Depends(require_roles(Role.APPROVER, Role.BUDGET_ADMIN))):
    requests = approvals_inbox(UnitOfWork())
    return [
        RequestResponse(
            id=req.id,
            plan_id=req.plan_id,
            requested_amount=req.requested_amount,
            status=req.status.value,
        )
        for req in requests
    ]


@router.post("/approvals/{request_id}/approve", response_model=RequestResponse)
def post_approve(
    request_id: int,
    reason: str,
    approved_by: str,
    _user: CurrentUser = Depends(require_roles(Role.APPROVER, Role.BUDGET_ADMIN)),
):
    try:
        request = approve_request(UnitOfWork(), request_id, reason=reason, approved_by=approved_by)
    except BudgetOverrun as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return RequestResponse(
        id=request.id,
        plan_id=request.plan_id,
        requested_amount=request.requested_amount,
        status=request.status.value,
    )


@router.post("/approvals/{request_id}/return", response_model=RequestResponse)
def post_return(request_id: int, _user: CurrentUser = Depends(require_roles(Role.APPROVER, Role.BUDGET_ADMIN))):
    request = return_request(UnitOfWork(), request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return RequestResponse(
        id=request.id,
        plan_id=request.plan_id,
        requested_amount=request.requested_amount,
        status=request.status.value,
    )


@router.post("/approvals/{request_id}/reject", response_model=RequestResponse)
def post_reject(request_id: int, _user: CurrentUser = Depends(require_roles(Role.APPROVER, Role.BUDGET_ADMIN))):
    request = reject_request(UnitOfWork(), request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return RequestResponse(
        id=request.id,
        plan_id=request.plan_id,
        requested_amount=request.requested_amount,
        status=request.status.value,
    )


@router.post("/executions", response_model=ExecutionResponse)
def post_execution(payload: ExecutionCreate, _user: CurrentUser = Depends(require_roles(Role.USER, Role.BUDGET_ADMIN))):
    execution = create_execution(UnitOfWork(), payload)
    return ExecutionResponse(
        id=execution.id,
        request_id=execution.request_id,
        status=execution.status.value,
        actual_amount=execution.actual_amount,
    )


@router.get("/executions", response_model=list[ExecutionResponse])
def get_executions(
    status: ExecutionStatus | None = None,
    _user: CurrentUser = Depends(require_roles(Role.USER, Role.BUDGET_ADMIN)),
):
    executions = list_executions(UnitOfWork(), status=status)
    return [
        ExecutionResponse(
            id=exec_.id,
            request_id=exec_.request_id,
            status=exec_.status.value,
            actual_amount=exec_.actual_amount,
        )
        for exec_ in executions
    ]


@router.post("/executions/{execution_id}/set-ordered", response_model=ExecutionResponse)
def post_execution_ordered(
    execution_id: int, _user: CurrentUser = Depends(require_roles(Role.USER, Role.BUDGET_ADMIN))
):
    execution = set_execution_status(UnitOfWork(), execution_id, ExecutionStatus.ORDERED)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return ExecutionResponse(
        id=execution.id,
        request_id=execution.request_id,
        status=execution.status.value,
        actual_amount=execution.actual_amount,
    )


@router.post("/executions/{execution_id}/set-delivered", response_model=ExecutionResponse)
def post_execution_delivered(
    execution_id: int, _user: CurrentUser = Depends(require_roles(Role.USER, Role.BUDGET_ADMIN))
):
    execution = set_execution_status(UnitOfWork(), execution_id, ExecutionStatus.DELIVERED)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return ExecutionResponse(
        id=execution.id,
        request_id=execution.request_id,
        status=execution.status.value,
        actual_amount=execution.actual_amount,
    )


@router.post("/executions/{execution_id}/set-invoiced", response_model=ExecutionResponse)
def post_execution_invoiced(
    execution_id: int, _user: CurrentUser = Depends(require_roles(Role.USER, Role.BUDGET_ADMIN))
):
    execution = set_execution_status(UnitOfWork(), execution_id, ExecutionStatus.INVOICED)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return ExecutionResponse(
        id=execution.id,
        request_id=execution.request_id,
        status=execution.status.value,
        actual_amount=execution.actual_amount,
    )


@router.post("/executions/{execution_id}/set-paid", response_model=ExecutionResponse)
def post_execution_paid(
    execution_id: int,
    payload: ExecutionPaid,
    _user: CurrentUser = Depends(require_roles(Role.USER, Role.BUDGET_ADMIN)),
):
    try:
        execution = mark_execution_paid(UnitOfWork(), execution_id, payload)
    except BudgetOverrun as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return ExecutionResponse(
        id=execution.id,
        request_id=execution.request_id,
        status=execution.status.value,
        actual_amount=execution.actual_amount,
    )


@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    fiscal_year: int,
    department_id: int,
    _user: CurrentUser = Depends(require_roles(Role.USER, Role.APPROVER, Role.BUDGET_ADMIN, Role.AUDITOR)),
):
    summary = dashboard_summary(UnitOfWork(), fiscal_year=fiscal_year, department_id=department_id)
    return DashboardSummaryResponse(**summary)


@router.get("/reports/budget-summary", response_model=list[BudgetSummaryRow])
def get_report_budget_summary(
    fiscal_year: int,
    department_id: int,
    _user: CurrentUser = Depends(require_roles(Role.USER, Role.APPROVER, Role.BUDGET_ADMIN, Role.AUDITOR)),
):
    summary = report_budget_summary(UnitOfWork(), fiscal_year=fiscal_year, department_id=department_id)
    return [BudgetSummaryRow(**row) for row in summary]


@router.get("/reports/monthly-summary", response_model=list[MonthlySummaryRow])
def get_report_monthly_summary(
    fiscal_year: int,
    department_id: int,
    _user: CurrentUser = Depends(require_roles(Role.USER, Role.APPROVER, Role.BUDGET_ADMIN, Role.AUDITOR)),
):
    summary = report_monthly_summary(UnitOfWork(), fiscal_year=fiscal_year, department_id=department_id)
    return [MonthlySummaryRow(**row) for row in summary]


@router.get("/reports/unplanned-requests", response_model=UnplannedRequestSummary)
def get_report_unplanned_requests(
    _user: CurrentUser = Depends(require_roles(Role.USER, Role.APPROVER, Role.BUDGET_ADMIN, Role.AUDITOR))
):
    summary = report_unplanned_requests(UnitOfWork())
    return UnplannedRequestSummary(**summary)


@router.get("/audit-logs", response_model=list[AuditLogResponse])
def get_audit_logs(
    actor: str | None = None,
    action: str | None = None,
    target_type: str | None = None,
    target_id: int | None = None,
    _user: CurrentUser = Depends(require_roles(Role.AUDITOR, Role.BUDGET_ADMIN)),
):
    logs = list_audit_logs(UnitOfWork(), actor=actor, action=action, target_type=target_type, target_id=target_id)
    return [
        AuditLogResponse(
            id=log.id,
            actor=log.actor,
            action=log.action,
            target_type=log.target_type,
            target_id=log.target_id,
            reason=log.reason,
            detail_json=log.detail_json,
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]


@router.get("/audit-logs/recent", response_model=list[AuditLogResponse])
def get_recent_audit_logs(
    limit: int = 10,
    _user: CurrentUser = Depends(require_roles(Role.AUDITOR, Role.BUDGET_ADMIN)),
):
    logs = recent_audit_logs(UnitOfWork(), limit=limit)
    return [
        AuditLogResponse(
            id=log.id,
            actor=log.actor,
            action=log.action,
            target_type=log.target_type,
            target_id=log.target_id,
            reason=log.reason,
            detail_json=log.detail_json,
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]


@router.get("/categories", response_model=list[CategoryResponse])
def get_categories(_user: CurrentUser = Depends(require_roles(Role.USER, Role.BUDGET_ADMIN))):
    categories = list_categories(UnitOfWork())
    return [CategoryResponse(id=c.id, name=c.name) for c in categories]


@router.post("/categories", response_model=CategoryResponse)
def post_category(
    payload: CategoryCreate,
    _user: CurrentUser = Depends(require_roles(Role.BUDGET_ADMIN)),
):
    category = create_category(UnitOfWork(), payload)
    return CategoryResponse(id=category.id, name=category.name)


@router.put("/categories/{category_id}")
def put_category(
    category_id: int,
    payload: CategoryUpdate,
    _user: CurrentUser = Depends(require_roles(Role.BUDGET_ADMIN)),
):
    updated = update_category(UnitOfWork(), category_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"status": "ok"}


@router.delete("/categories/{category_id}")
def delete_category_endpoint(
    category_id: int,
    _user: CurrentUser = Depends(require_roles(Role.BUDGET_ADMIN)),
):
    deleted = delete_category(UnitOfWork(), category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"status": "ok"}


@router.get("/subcategories", response_model=list[SubcategoryResponse])
def get_subcategories(
    category_id: int | None = None,
    _user: CurrentUser = Depends(require_roles(Role.USER, Role.BUDGET_ADMIN)),
):
    subs = list_subcategories(UnitOfWork(), category_id=category_id)
    return [SubcategoryResponse(id=s.id, category_id=s.category_id, name=s.name) for s in subs]


@router.post("/subcategories", response_model=SubcategoryResponse)
def post_subcategory(
    payload: SubcategoryCreate,
    _user: CurrentUser = Depends(require_roles(Role.BUDGET_ADMIN)),
):
    sub = create_subcategory(UnitOfWork(), payload)
    return SubcategoryResponse(id=sub.id, category_id=sub.category_id, name=sub.name)


@router.put("/subcategories/{subcategory_id}")
def put_subcategory(
    subcategory_id: int,
    payload: SubcategoryUpdate,
    _user: CurrentUser = Depends(require_roles(Role.BUDGET_ADMIN)),
):
    updated = update_subcategory(UnitOfWork(), subcategory_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    return {"status": "ok"}


@router.delete("/subcategories/{subcategory_id}")
def delete_subcategory_endpoint(
    subcategory_id: int,
    _user: CurrentUser = Depends(require_roles(Role.BUDGET_ADMIN)),
):
    deleted = delete_subcategory(UnitOfWork(), subcategory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    return {"status": "ok"}
