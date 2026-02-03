from __future__ import annotations

from decimal import Decimal
from pydantic import BaseModel, Field

from app.domain.enums import PlanStatus


class BudgetCreate(BaseModel):
    fiscal_year: int
    department_id: int
    category_id: int
    initial_amount: Decimal = Field(gt=0)


class BudgetAdjustmentCreate(BaseModel):
    amount: Decimal
    reason: str
    created_by: str


class PlanCreate(BaseModel):
    fiscal_year: int
    department_id: int
    category_id: int
    subcategory_id: int
    product_name: str
    vendor: str
    planned_month: str
    contract_type: str
    amount: Decimal = Field(gt=0)
    plan_type: str
    note: str


class PlanBulkCreate(BaseModel):
    plans: list[PlanCreate]


class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    name: str


class SubcategoryCreate(BaseModel):
    category_id: int
    name: str


class SubcategoryUpdate(BaseModel):
    category_id: int
    name: str


class PlanUpdate(BaseModel):
    category_id: int = Field(gt=0)
    subcategory_id: int = Field(gt=0)
    product_name: str
    vendor: str
    planned_month: str
    contract_type: str
    amount: Decimal = Field(gt=0)
    plan_type: str
    note: str
    status: PlanStatus
    changed_by: str
    reason: str


class RequestCreate(BaseModel):
    plan_id: int | None = None
    requested_amount: Decimal = Field(gt=0)
    created_by: str
    reason: str


class ExecutionCreate(BaseModel):
    request_id: int


class ExecutionPaid(BaseModel):
    actual_amount: Decimal = Field(gt=0)
    allow_over: bool = False
    reason: str
    paid_by: str
