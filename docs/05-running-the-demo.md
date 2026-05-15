# Part 5 — Running the demo end to end

> *Audience: anyone who wants to spin up the demo on their laptop, walk through it with a customer, or extend it with another locale.*

This guide takes you from a clean checkout to a working three-service stack, a five-language UI, and a documented script for showing the demo to a customer. It also explains how to add or update a locale without redeploying, and how to run the test suite.

## What you will end up with

Three containers running side by side on your machine:

- **`compliant-backend`** on `http://localhost:8000` — the EU AI Act-compliant FastAPI app with the Articles 8–15 controls wired in.
- **`traditional-backend`** on `http://localhost:8001` — the "just call the model" baseline.
- **`compliant-frontend`** on `http://localhost:5173` — the React UI that renders both stacks side by side with the compliance sidecar.

A 5-language UI (EN, DE, FR, ES, IT), an Article 50 candidate-disclosure endpoint that responds in the requested locale, and a `patch_locale.py` CLI you can use to add a sixth locale in under a minute.

## Prerequisites

- Docker Desktop (or Docker Engine + Compose v2) for the one-command path.
- Or: Python 3.11+ and Node.js 20+ for the direct path.

The compliant backend ships with a deterministic stub model so **no API keys are required** to run the demo.

## One-command spin-up (recommended)

From the repository root:

```bash
docker compose up --build
```

Wait for the three healthchecks to go green, then open `http://localhost:5173`.

## Direct (no Docker) run

Three terminals, run from the repository root.

```bash
# Terminal 1 — compliant backend
cd backend
pip install -r requirements.txt
PYTHONPATH=.:.. uvicorn app.main:app --port 8000 --reload

# Terminal 2 — traditional baseline
cd traditional-stack
pip install -r requirements.txt
uvicorn app:app --port 8001 --reload

# Terminal 3 — frontend
cd frontend
npm install
npm run dev
```

The `PYTHONPATH=.:..` on the compliant backend lets `from i18n import loader` resolve from the repo root.

## The customer-facing walkthrough (15 minutes)

Use this script when demoing to a customer. It is sequenced so the compliance delta becomes visible piece by piece — not as a feature list, but as evidence the customer can see being produced live.

### 0. Set the stage (1 minute)

Open `http://localhost:5173`. Point at the two panels.

> *"Both backends do CV screening for the same job and the same candidate. The traditional stack — what most teams ship today — gives you the answer. The compliant stack gives you the answer plus the evidence the EU AI Act requires for a high-risk system. Today, you ship the left side. After August 2026, if you operate in the EU and your use case is high-risk, you ship the right side."*

Switch the language picker to German. Point out that **the UI, the panel copy, the compliance sidecar, and the candidate-disclosure text all switch language together**. Then switch back to English (or to whichever language the customer prefers).

### 1. Run the same input through both stacks (1 minute)

Pick "Backend Engineer (DE)" as the job and "Candidate A — strong match" as the CV. Click "Run both stacks".

- The **traditional panel** returns a JSON blob with a recommendation, a score, and nothing else.
- The **compliant panel** returns the same recommendation and score, plus a confidence, an explanation, and a **compliance envelope**: intended-purpose checked, input pseudonymised, audit event written, bias metrics refreshed, two-person oversight required.

> *"Same answer. Different evidence."*

### 2. Show Article 14 — human oversight (3 minutes)

Open the Oversight tab in the compliance sidecar. Walk through the controls:

- **Reviewer ID** — every action is attributed.
- **Action** — `accept` / `override` / `do_not_use`.
- **Rationale** — required, minimum 10 characters. Try submitting with a 5-character rationale; the backend rejects it. *"Article 14 expects meaningful oversight; the system enforces it."*
- Submit a real accept. Watch the history append.
- Try to accept again with the **same** reviewer ID. The backend rejects it. *"Article 14 plus the deployer's policy: two-person review."*
- Use a second reviewer ID. The action succeeds.

### 3. Show Article 12 — the audit log (3 minutes)

Switch to the Audit tab. Point at the events that have accumulated: the screening decision, the oversight actions, all written by the system itself.

- Each row shows the timestamp, event type, actor, subject (pseudonymised), and a truncated event hash.
- The **"Chain verification: OK"** banner at the top is computed live — it replays the chain and confirms every event hashes to its predecessor.

If you want to make the point about tamper evidence more concrete, you can demonstrate the chain breaking. Open a shell into the backend, edit one event row in the SQLite store, and reload — the verification banner flips to **BROKEN** and identifies the row.

```bash
# in the running container
docker exec -it compliant-backend sh -c \
  "sqlite3 /app/data/compliance.db 'UPDATE compliance_events SET payload=json_set(payload, \"\$.data.score\", 0.99) WHERE id=1;'"
```

Then click Reload Audit in the UI (or `POST /compliance/audit-log/verify` from the OpenAPI page) — the chain reports broken.

### 4. Show Article 13 — the model card (2 minutes)

Switch to the Model card tab. The card is generated from the **same live state the system runs on**. Point at:

- The risk classification with its Annex III basis.
- The declared accuracy, per locale.
- The known limitations.
- The dataset section with provenance and licence basis.
- The top risks with residual exposure.
- The contact for redress.

> *"This is what your deployer customers receive. This is what their auditor reviews. This is what the candidate's lawyer would ask for after a complaint. It is generated, not maintained by hand — so it cannot drift from the system."*

### 5. Show Article 15 / 72 — the bias monitor (3 minutes)

Switch to the Bias monitor tab. If you've only made one or two requests, the table will be sparse — run a few more decisions first, ideally with a mix of "Candidate A — strong match (locale=de)" and "Candidate C — weak match (locale=en)". This generates a meaningful skew across pseudonymised cohorts.

Click **Recompute now**. The selection-rate deltas appear, with any breach of the 0.10 threshold marked `ALERT`. Switch back to the Audit tab — a new `bias_alert` event has been written by the system itself.

> *"Article 15 plus Article 72. The system raises the flag and writes the evidence. No one has to remember to run a report."*

### 6. Show the Annex IV technical documentation pack (1 minute)

Open `http://localhost:8000/compliance/technical-documentation.md` in a new tab. Scroll through the eight Annex IV headings — general description, development process, monitoring and control, risk-management system, lifecycle changes, harmonised standards applied, declaration of conformity, post-market monitoring.

> *"This is what a conformity assessment file looks like. Generated, not assembled by hand, from the same sources the live system runs on. Every change to the risk register, the data lineage, or the intended purpose shows up here on the next request."*

### 7. Show Article 50 — the candidate-facing disclosure (1 minute)

Open in a new tab:
- `http://localhost:8000/compliance/candidate-disclosure?lang=en`
- `http://localhost:8000/compliance/candidate-disclosure?lang=de`
- `http://localhost:8000/compliance/candidate-disclosure?lang=fr`

Each returns the Article 50 disclosure copy in the requested locale, with a contact for redress. *"This is what gets surfaced to the candidate. The deployer cannot ship the system without including it."*

### Close (1 minute)

> *"The traditional stack ships the model. The compliant stack ships the model and the evidence around it. The Act treats the AI system as a lifecycle — design, data, training, deployment, oversight, monitoring, change management — and expects each stage to produce its own evidence. The architecture you saw today is one way to make that real. Your team can swap the model, swap the frontend, swap the data store — and the regulated artefacts stay intact."*

## Exercising the i18n machinery

The seed set is EN, DE, FR, ES, IT. To add a locale at runtime without redeploying:

```bash
# 1. Scaffold a new locale with the same keys as English, empty values.
python i18n/patch_locale.py create nl --name Nederlands

# 2. Set values one key at a time, or open i18n/locales/nl.json and edit it.
python i18n/patch_locale.py set nl ui.run_button "Beide stacks uitvoeren"
python i18n/patch_locale.py set nl panels.traditional_title "Traditionele stack"
# ... etc

# 3. Confirm the locale has no missing keys relative to English.
python i18n/patch_locale.py validate nl

# 4. Tell the running backend to refresh its cache. No restart required.
python i18n/patch_locale.py reload --api http://localhost:8000

# 5. Hard-refresh the frontend. The new language appears in the picker.
```

Updates to an existing locale follow the same pattern, minus step 1.

> **Production translation note**: the seed locales are functional but have **not** been reviewed by professional linguists or legal counsel. Before going live, have each locale reviewed for HR-tech and regulatory tone, and have the Article 50 disclosure copy reviewed by counsel in each jurisdiction.

## Running the test suite

From the repository root:

```bash
pip install -r backend/requirements.txt pytest httpx
PYTHONPATH=backend:. pytest tests/ -v
```

Two test files run:

- `tests/test_smoke.py` — covers the API surface. The compliant root endpoint, healthcheck, screening + compliance envelope, decision lookup, every compliance read endpoint, and the i18n routes (locale list + locale-aware candidate disclosure).
- `tests/test_compliance.py` — one focused test per Article 8–15 control. Each test asserts that the control is wired and produces evidence the EU AI Act expects.

The tests run in-process via FastAPI's `TestClient`, against a temporary SQLite database created by the `tmp_db_path` fixture. They use the stub model layer, so they require no external API keys.

Expected output:

```
tests/test_smoke.py::test_root PASSED
tests/test_smoke.py::test_health PASSED
tests/test_smoke.py::test_screening_returns_envelope PASSED
... (and so on)
tests/test_compliance.py::test_article_8_intended_purpose_declared PASSED
tests/test_compliance.py::test_article_9_risk_register_populated PASSED
... (and so on)
```

A failing test should be treated as a wiring regression — the control either was not produced or produced unrecognised evidence — and should block release until fixed.

## Troubleshooting

**The frontend cannot reach the backend.** Confirm the backend healthcheck has passed (`docker compose ps` or `curl http://localhost:8000/health`). Confirm `VITE_COMPLIANT_API` matches the URL you see in your browser; the default is `http://localhost:8000`.

**The bias monitor table is empty.** It populates only once you have at least five decisions in a pseudonymised cohort. Run more decisions or lower `BIAS_ALERT_THRESHOLD` for the demo.

**Two-person oversight is rejecting my second action even with a different reviewer.** Check that you actually changed the Reviewer ID field; the UI does not auto-rotate it.

**A new locale doesn't appear in the language picker.** Hit `POST /i18n/reload` (or `python i18n/patch_locale.py reload`), then hard-refresh the browser. The locale file must live under `i18n/locales/{locale}.json` and must be valid JSON.

**The audit chain shows BROKEN immediately.** Check that the `compliance_events` table has not been touched outside the application, and that the volume mount in `docker-compose.yml` matches `COMPLIANCE_DB_PATH`. If you deliberately corrupted a row for demonstration, revert it.

## Where to go from here

The architecture document (`docs/04-architecture.md`) maps every obligation to the file that implements it. The operational document (`docs/03-operational-aspects.md`) maps every obligation to the operating practice that runs it. Use them together when extending the demo to your real use case.

Two natural next steps for a production-bound team:

1. **Replace the use case.** Substitute the CV-screening domain logic in `backend/app/services/cv_parser.py` and `backend/app/api/screening.py`, update `system_intended_purpose.yaml`, re-seed the risk register and data lineage, and you have the same compliance scaffolding for any other high-risk use case.
2. **Swap the model.** Set `LITELLM_PROVIDER` and `LITELLM_MODEL` and the typed-output contract in `services/llm_client.py` ensures the controls keep working without any change to the surrounding code.

The point of the compliant pattern is that the regulated artefacts are independent of the model and of the use case. The scaffolding survives both.
