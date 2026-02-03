from __future__ import annotations

from contextlib import AbstractContextManager

from sqlalchemy.orm import Session

from app.infrastructure.db import SessionLocal
from app.infrastructure.repositories import (
    AuditLogRepository,
    BudgetRepository,
    BudgetTransactionRepository,
    CategoryRepository,
    ExecutionRepository,
    PlanRepository,
    RequestRepository,
    SubcategoryRepository,
)


class UnitOfWork(AbstractContextManager):
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory
        self.session: Session | None = None
        self.budgets: BudgetRepository
        self.plans: PlanRepository
        self.requests: RequestRepository
        self.executions: ExecutionRepository
        self.transactions: BudgetTransactionRepository
        self.audit_logs: AuditLogRepository
        self.categories: CategoryRepository
        self.subcategories: SubcategoryRepository

    def __enter__(self):
        self.session = self.session_factory()
        self.budgets = BudgetRepository(self.session)
        self.plans = PlanRepository(self.session)
        self.requests = RequestRepository(self.session)
        self.executions = ExecutionRepository(self.session)
        self.transactions = BudgetTransactionRepository(self.session)
        self.audit_logs = AuditLogRepository(self.session)
        self.categories = CategoryRepository(self.session)
        self.subcategories = SubcategoryRepository(self.session)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.session is None:
            return False
        if exc:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()
        return False
