import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.db import Base
from app.infrastructure.unit_of_work import UnitOfWork


@pytest.fixture()
def uow_sqlite():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    return UnitOfWork(session_factory=SessionLocal)
