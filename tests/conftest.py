import os
import tempfile

os.environ["EXPENSE_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")

import pytest
from fastapi.testclient import TestClient

from app import db
from app.main import app


@pytest.fixture(autouse=True)
def clean_db():
    with db.get_conn() as conn:
        conn.execute("DELETE FROM expenses")
    yield


@pytest.fixture
def client():
    return TestClient(app)
