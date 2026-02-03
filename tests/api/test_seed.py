from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.enums import BudgetTxType, ExecutionStatus, PlanStatus, RequestStatus
from app.infrastructure.db import Base
from app.infrastructure import models
from app.infrastructure.seed import seed_sample_data


def test_seed_sample_data_two_years():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    with SessionLocal() as session:
        seed_sample_data(session)
        assert session.query(models.CategoryModel).count() == 4
        assert session.query(models.SubcategoryModel).count() == 9
        assert session.query(models.BudgetModel).count() == 8
        assert session.query(models.PlanModel).count() == 192
        assert session.query(models.RequestModel).count() == 12
        assert session.query(models.ExecutionModel).count() == 6

        plan_statuses = {row[0] for row in session.query(models.PlanModel.status).distinct().all()}
        request_statuses = {row[0] for row in session.query(models.RequestModel.status).distinct().all()}
        execution_statuses = {row[0] for row in session.query(models.ExecutionModel.status).distinct().all()}
        tx_types = {row[0] for row in session.query(models.BudgetTransactionModel.tx_type).distinct().all()}

        assert plan_statuses == {status.value for status in PlanStatus}
        assert request_statuses == {status.value for status in RequestStatus}
        assert execution_statuses == {status.value for status in ExecutionStatus}
        assert tx_types == {tx.value for tx in BudgetTxType}

        assert session.query(models.RequestModel).filter(models.RequestModel.plan_id.is_(None)).count() == 1
        assert session.query(models.RequestModel).filter(models.RequestModel.plan_id.isnot(None)).count() >= 1
        assert session.query(models.BudgetAdjustmentModel).count() >= 1
        assert session.query(models.PlanChangeModel).count() >= 1
        assert session.query(models.BudgetTransactionModel).filter(models.BudgetTransactionModel.request_id.is_(None)).count() >= 1
        assert session.query(models.AuditLogModel).filter(models.AuditLogModel.reason.is_(None)).count() >= 1
        assert session.query(models.ExecutionModel).filter(models.ExecutionModel.actual_amount.is_(None)).count() >= 1
        assert session.query(models.ExecutionModel).filter(models.ExecutionModel.actual_amount > 0).count() >= 1
        assert session.query(models.ExecutionModel).filter(models.ExecutionModel.status == ExecutionStatus.PAID.value).count() >= 1
        assert (
            session.query(models.ExecutionModel)
            .filter(models.ExecutionModel.status == ExecutionStatus.PAID.value)
            .filter(models.ExecutionModel.actual_amount > 0)
            .count()
            >= 1
        )
        assert (
            session.query(models.BudgetTransactionModel)
            .filter(models.BudgetTransactionModel.tx_type == BudgetTxType.ACTUALIZE.value)
            .count()
            >= 1
        )
        assert (
            session.query(models.BudgetTransactionModel)
            .filter(models.BudgetTransactionModel.tx_type == BudgetTxType.REVERT_ACTUAL.value)
            .count()
            >= 1
        )

        seed_sample_data(session)
        assert session.query(models.CategoryModel).count() == 4
        assert session.query(models.PlanModel).count() == 192
