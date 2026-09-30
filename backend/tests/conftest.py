import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 — registers models on Base.metadata
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.storage import get_storage


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    """Point document storage at a per-test temp dir instead of the real
    ./data/uploads, and reset the cached Settings/storage singletons so the
    override actually takes effect."""
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path / "uploads"))
    get_settings.cache_clear()
    get_storage.cache_clear()
    yield
    get_settings.cache_clear()
    get_storage.cache_clear()


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
