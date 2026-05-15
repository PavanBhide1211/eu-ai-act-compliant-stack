"""Shared pytest fixtures.

Spins the compliant backend up in-process against a temporary SQLite database
so tests do not contaminate any developer's local data.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
# Make `app.*` importable when running pytest from the repo root.
for p in (str(BACKEND_DIR), str(REPO_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)


@pytest.fixture(scope="session")
def tmp_db_path(tmp_path_factory):
    p = tmp_path_factory.mktemp("compliance-db") / "compliance.db"
    return p


@pytest.fixture(scope="session")
def client(tmp_db_path):
    # Configure the backend to use the temp DB *before* importing the app.
    os.environ["COMPLIANCE_DB_PATH"] = str(tmp_db_path)
    # Use the deterministic stub model so tests have no external dependencies.
    os.environ["LITELLM_PROVIDER"] = "stub"
    os.environ["LITELLM_MODEL"] = "stub-cv-scorer-v1"
    os.environ["REQUIRE_TWO_PERSON_OVERSIGHT"] = "true"
    # Lower the bias threshold so a small synthetic skew is enough to trigger.
    os.environ["BIAS_ALERT_THRESHOLD"] = "0.05"

    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_request_payload():
    return {
        "cv": {
            "skills": ["python", "fastapi", "postgres", "docker"],
            "years_experience": 4,
            "locale": "en",
            "role_family": "engineering",
        },
        "job": {
            "title": "Backend Engineer",
            "required_skills": ["python", "fastapi", "postgres", "docker"],
            "min_years_experience": 3,
            "locale": "en",
            "role_family": "engineering",
        },
        "deployer_id": "test-deployer",
        "requested_by_user": "test-user@example.eu",
    }
