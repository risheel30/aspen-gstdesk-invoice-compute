import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.seed import load_seed


@pytest.fixture
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=eng)
    return eng


@pytest.fixture
def db(engine):
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSession()
    load_seed(session)
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(engine, db):
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        s = TestingSession()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_risheel():
    return {"X-Vendor-GSTIN": "27ABCPS1234A1Z5"}


@pytest.fixture
def auth_vaibhav():
    return {"X-Vendor-GSTIN": "29AAFCV9876B1Z2"}


@pytest.fixture
def auth_priya():
    return {"X-Vendor-GSTIN": "33APMPM4567C2Z8"}
