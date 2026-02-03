from decimal import Decimal

import pytest

from app.domain.entities import Budget, Request, Execution
from app.domain.enums import ExecutionStatus
from app.domain.errors import BudgetOverrun, InvalidStatusTransition
from app.domain.services import create_actualize_txs, create_commit_tx


def test_remaining_budget_calculation():
    budget = Budget(
        id=1,
        fiscal_year=2026,
        department_id=1,
        category_id=1,
        initial_amount=Decimal("1000"),
        adjustments=[],
    )
    remaining = budget.remaining(commit_total=Decimal("200"), actual_total=Decimal("100"))
    assert remaining == Decimal("700")


def test_commit_transaction_created_on_approval():
    request = Request(id=10, plan_id=1, requested_amount=Decimal("300"))
    tx = create_commit_tx(budget_id=5, request=request, reason="approve", created_by="alice")
    assert tx.amount == Decimal("300")
    assert tx.budget_id == 5
    assert tx.request_id == 10


def test_actualize_and_uncommit_transactions_on_paid():
    txs = create_actualize_txs(
        budget_id=1,
        request_id=2,
        requested_amount=Decimal("500"),
        actual_amount=Decimal("450"),
        reason="paid",
        created_by="bob",
    )
    assert len(txs) == 2
    assert txs[0].amount == Decimal("450")
    assert txs[1].amount == Decimal("50")


def test_execution_status_transition_and_overrun():
    execution = Execution(id=1, request_id=1)
    execution.set_status(ExecutionStatus.ORDERED)
    execution.set_status(ExecutionStatus.DELIVERED)
    execution.set_status(ExecutionStatus.INVOICED)

    with pytest.raises(BudgetOverrun):
        execution.mark_paid(Decimal("120"), Decimal("100"), allow_over=False)

    diff = execution.mark_paid(Decimal("100"), Decimal("120"), allow_over=True)
    assert diff == Decimal("20")


def test_request_invalid_transition():
    request = Request(id=1, plan_id=1, requested_amount=Decimal("100"))
    with pytest.raises(InvalidStatusTransition):
        request.approve()
