from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.domain.enums import BudgetTxType, ExecutionStatus, PlanStatus, RequestStatus
from app.domain.errors import BudgetOverrun, InvalidStatusTransition


@dataclass
class BudgetAdjustment:
    amount: Decimal
    reason: str
    created_by: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Budget:
    id: Optional[int]
    fiscal_year: int
    department_id: int
    category_id: int
    initial_amount: Decimal
    adjustments: list[BudgetAdjustment] = field(default_factory=list)

    def total_limit(self) -> Decimal:
        total = self.initial_amount
        for adj in self.adjustments:
            total += adj.amount
        return total

    def remaining(self, commit_total: Decimal, actual_total: Decimal) -> Decimal:
        return self.total_limit() - commit_total - actual_total


@dataclass
class Plan:
    id: Optional[int]
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
    status: PlanStatus = PlanStatus.ACTIVE


@dataclass
class PlanChange:
    id: Optional[int]
    plan_id: int
    changed_by: str
    reason: str
    diff_json: dict
    changed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Request:
    id: Optional[int]
    plan_id: Optional[int]
    requested_amount: Decimal
    status: RequestStatus = RequestStatus.DRAFT

    def submit(self) -> None:
        if self.status != RequestStatus.DRAFT:
            raise InvalidStatusTransition("Only DRAFT can be submitted")
        self.status = RequestStatus.SUBMITTED

    def approve(self) -> None:
        if self.status != RequestStatus.SUBMITTED:
            raise InvalidStatusTransition("Only SUBMITTED can be approved")
        self.status = RequestStatus.APPROVED

    def return_request(self) -> None:
        if self.status != RequestStatus.SUBMITTED:
            raise InvalidStatusTransition("Only SUBMITTED can be returned")
        self.status = RequestStatus.RETURNED

    def reject(self) -> None:
        if self.status != RequestStatus.SUBMITTED:
            raise InvalidStatusTransition("Only SUBMITTED can be rejected")
        self.status = RequestStatus.REJECTED


@dataclass
class Execution:
    id: Optional[int]
    request_id: int
    status: ExecutionStatus = ExecutionStatus.NOT_STARTED
    actual_amount: Optional[Decimal] = None

    def set_status(self, new_status: ExecutionStatus) -> None:
        valid = {
            ExecutionStatus.NOT_STARTED: {ExecutionStatus.ORDERED, ExecutionStatus.CANCELED},
            ExecutionStatus.ORDERED: {ExecutionStatus.DELIVERED, ExecutionStatus.CANCELED},
            ExecutionStatus.DELIVERED: {ExecutionStatus.INVOICED, ExecutionStatus.CANCELED},
            ExecutionStatus.INVOICED: {ExecutionStatus.PAID, ExecutionStatus.CANCELED},
            ExecutionStatus.PAID: set(),
            ExecutionStatus.CANCELED: set(),
        }
        if new_status not in valid[self.status]:
            raise InvalidStatusTransition(f"{self.status} -> {new_status} is not allowed")
        self.status = new_status

    def mark_paid(self, actual_amount: Decimal, requested_amount: Decimal, allow_over: bool = False) -> Decimal:
        if self.status != ExecutionStatus.INVOICED:
            raise InvalidStatusTransition("Only INVOICED can be paid")
        if actual_amount > requested_amount and not allow_over:
            raise BudgetOverrun("Actual amount exceeds requested amount")
        self.actual_amount = actual_amount
        self.status = ExecutionStatus.PAID
        return requested_amount - actual_amount


@dataclass
class BudgetTransaction:
    id: Optional[int]
    budget_id: int
    request_id: Optional[int]
    tx_type: BudgetTxType
    amount: Decimal
    reason: str
    created_by: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Category:
    id: Optional[int]
    name: str


@dataclass
class Subcategory:
    id: Optional[int]
    category_id: int
    name: str


@dataclass
class AuditLog:
    id: Optional[int]
    actor: str
    action: str
    target_type: str
    target_id: Optional[int]
    reason: Optional[str]
    detail_json: dict
    created_at: datetime = field(default_factory=datetime.utcnow)
