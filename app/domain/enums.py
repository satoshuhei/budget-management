from __future__ import annotations

from enum import Enum


class PlanStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class RequestStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    RETURNED = "RETURNED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELED = "CANCELED"
    CLOSED = "CLOSED"


class ExecutionStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    ORDERED = "ORDERED"
    DELIVERED = "DELIVERED"
    INVOICED = "INVOICED"
    PAID = "PAID"
    CANCELED = "CANCELED"


class BudgetTxType(str, Enum):
    COMMIT = "COMMIT"
    UNCOMMIT = "UNCOMMIT"
    ACTUALIZE = "ACTUALIZE"
    REVERT_ACTUAL = "REVERT_ACTUAL"


class Role(str, Enum):
    USER = "USER"
    APPROVER = "APPROVER"
    BUDGET_ADMIN = "BUDGET_ADMIN"
    AUDITOR = "AUDITOR"
