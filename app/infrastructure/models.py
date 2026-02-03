from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import BudgetTxType, ExecutionStatus, PlanStatus, RequestStatus
from app.infrastructure.db import Base


class BudgetModel(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fiscal_year: Mapped[int] = mapped_column(Integer, index=True)
    department_id: Mapped[int] = mapped_column(Integer, index=True)
    category_id: Mapped[int] = mapped_column(Integer, index=True)
    initial_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    adjustments = relationship("BudgetAdjustmentModel", back_populates="budget", cascade="all, delete-orphan")


class BudgetAdjustmentModel(Base):
    __tablename__ = "budget_adjustments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    budget_id: Mapped[int] = mapped_column(ForeignKey("budgets.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    reason: Mapped[str] = mapped_column(String(255))
    created_by: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    budget = relationship("BudgetModel", back_populates="adjustments")


class PlanModel(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fiscal_year: Mapped[int] = mapped_column(Integer, index=True)
    department_id: Mapped[int] = mapped_column(Integer, index=True)
    category_id: Mapped[int] = mapped_column(Integer, index=True)
    subcategory_id: Mapped[int] = mapped_column(Integer, index=True)
    product_name: Mapped[str] = mapped_column(String(200))
    vendor: Mapped[str] = mapped_column(String(200))
    planned_month: Mapped[str] = mapped_column(String(7))
    contract_type: Mapped[str] = mapped_column(String(50))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    plan_type: Mapped[str] = mapped_column(String(50))
    note: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default=PlanStatus.ACTIVE.value)

    changes = relationship("PlanChangeModel", back_populates="plan", cascade="all, delete-orphan")


class PlanChangeModel(Base):
    __tablename__ = "plan_changes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))
    changed_by: Mapped[str] = mapped_column(String(100))
    reason: Mapped[str] = mapped_column(String(255))
    diff_json: Mapped[str] = mapped_column(String(2000))
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    plan = relationship("PlanModel", back_populates="changes")


class RequestModel(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    requested_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(20), default=RequestStatus.DRAFT.value)


class ExecutionModel(Base):
    __tablename__ = "executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default=ExecutionStatus.NOT_STARTED.value)
    actual_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)


class BudgetTransactionModel(Base):
    __tablename__ = "budget_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    budget_id: Mapped[int] = mapped_column(Integer)
    request_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tx_type: Mapped[str] = mapped_column(String(20))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    reason: Mapped[str] = mapped_column(String(255))
    created_by: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


class SubcategoryModel(Base):
    __tablename__ = "subcategories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    name: Mapped[str] = mapped_column(String(100))


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor: Mapped[str] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(50))
    target_type: Mapped[str] = mapped_column(String(50))
    target_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    detail_json: Mapped[str] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
