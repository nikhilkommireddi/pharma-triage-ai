import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.db.session import SessionLocal


def test_database_connectivity():
    """Integration test — requires the Postgres container from docker-compose.

    Run `docker compose up -d db` before running this test locally.
    """
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
    except OperationalError:
        pytest.skip("database is not reachable; start it with `docker compose up -d db`")
    finally:
        db.close()
