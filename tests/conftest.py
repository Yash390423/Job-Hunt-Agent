"""Pytest fixtures and test configuration."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = REPO_ROOT / "job_hunt_assistant"

for path in (str(REPO_ROOT), str(APP_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)


TEST_DB_PATH = Path(tempfile.gettempdir()) / "job_hunt_assistant_test.db"

os.environ["GEMINI_API_KEY"] = "test-gemini-key"
os.environ["ADZUNA_APP_ID"] = "test-adzuna-id"
os.environ["ADZUNA_APP_KEY"] = "test-adzuna-key"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ["LOG_LEVEL"] = "INFO"


@pytest.fixture(scope="session")
def env_vars():
    """Return the baseline test environment."""
    return {
        "GEMINI_API_KEY": os.environ["GEMINI_API_KEY"],
        "ADZUNA_APP_ID": os.environ["ADZUNA_APP_ID"],
        "ADZUNA_APP_KEY": os.environ["ADZUNA_APP_KEY"],
        "DATABASE_URL": os.environ["DATABASE_URL"],
    }


@pytest.fixture(autouse=True)
def clean_database():
    """Reset the SQLAlchemy database between tests."""
    from models.database import Base, create_tables, engine

    Base.metadata.drop_all(bind=engine)
    create_tables()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def mock_adzuna_response():
    """Sample Adzuna API payload."""
    return {
        "results": [
            {
                "title": "Data Analyst",
                "company": {"display_name": "Example Corp"},
                "location": {"display_name": "Bengaluru, India", "area": ["India", "Karnataka"]},
                "description": "Analyze data and build dashboards.",
                "redirect_url": "https://example.com/job/1",
            }
        ]
    }
