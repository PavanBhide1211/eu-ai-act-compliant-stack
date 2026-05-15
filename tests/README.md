# Tests

Two suites:

- `test_smoke.py` — basic API surface coverage on the compliant backend and the traditional baseline.
- `test_compliance.py` — one test per Article 8–15 control, verifying it is wired and produces the evidence the EU AI Act expects.

## Run

From the repo root, with the backend dependencies installed:

```bash
pip install -r backend/requirements.txt pytest httpx
PYTHONPATH=backend:. pytest tests/ -v
```

The tests use FastAPI's `TestClient`, so they don't need a running container — they spin the backend up in-process against a temporary SQLite DB.
