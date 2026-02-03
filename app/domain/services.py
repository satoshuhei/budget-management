from __future__ import annotations

from decimal import Decimal

from app.domain.entities import BudgetTransaction, Request
from app.domain.enums import BudgetTxType


def create_commit_tx(budget_id: int, request: Request, reason: str, created_by: str) -> BudgetTransaction:
    return BudgetTransaction(
        id=None,
        budget_id=budget_id,
        request_id=request.id,
        tx_type=BudgetTxType.COMMIT,
        amount=request.requested_amount,
        reason=reason,
        created_by=created_by,
    )


def create_actualize_txs(
    budget_id: int,
    request_id: int,
    requested_amount: Decimal,
    actual_amount: Decimal,
    reason: str,
    created_by: str,
) -> list[BudgetTransaction]:
    txs: list[BudgetTransaction] = [
        BudgetTransaction(
            id=None,
            budget_id=budget_id,
            request_id=request_id,
            tx_type=BudgetTxType.ACTUALIZE,
            amount=actual_amount,
            reason=reason,
            created_by=created_by,
        )
    ]
    diff = requested_amount - actual_amount
    if diff > 0:
        txs.append(
            BudgetTransaction(
                id=None,
                budget_id=budget_id,
                request_id=request_id,
                tx_type=BudgetTxType.UNCOMMIT,
                amount=diff,
                reason="Difference returned",
                created_by=created_by,
            )
        )
    return txs
