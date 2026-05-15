# Compliant Backend

FastAPI reference implementation of an EU AI Act-compliant CV screening API.

## Endpoints

- `POST /screening/score` — produces a recommendation **plus** a `compliance_envelope` describing the controls applied.
- `GET /compliance/intended-purpose` — Article 8 declared purpose.
- `GET /compliance/risk-register` — Article 9 risk-management entries.
- `GET /compliance/data-lineage` — Article 10 data-governance lineage.
- `GET /compliance/audit-log` — Article 12 chained event log + chain verification.
- `GET /compliance/model-card` — Article 13 model card (JSON).
- `GET /compliance/model-card.md` — Article 13 model card (markdown).
- `POST /compliance/oversight` — Article 14 reviewer action (accept / override / do_not_use).
- `GET /compliance/oversight/{request_id}` — oversight history for a decision.
- `GET /compliance/bias-monitor` — Article 15 / 72 subgroup metrics.
- `GET /compliance/technical-documentation.md` — Annex IV technical documentation pack.
- `GET /compliance/candidate-disclosure` — Article 50 transparency copy.

## Run

Inside docker-compose (recommended): `docker compose up backend`.

Locally:
```
pip install -r requirements.txt
uvicorn app.main:app --reload
```

OpenAPI is at `/docs`.

## Configuration

| Env var | Default | Purpose |
|---|---|---|
| `COMPLIANCE_DB_PATH` | `./data/compliance.db` | SQLite location |
| `LITELLM_PROVIDER` | `stub` | Set to `openai`, `anthropic`, `ollama`, etc. |
| `LITELLM_MODEL` | `stub-cv-scorer-v1` | Model identifier |
| `AUDIT_LOG_RETENTION_DAYS` | `365` | Article 12 retention |
| `BIAS_ALERT_THRESHOLD` | `0.10` | Subgroup selection-rate delta floor |
| `REQUIRE_TWO_PERSON_OVERSIGHT` | `true` | Article 14 two-person review |
