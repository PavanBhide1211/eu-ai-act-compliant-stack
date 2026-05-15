# Build Progress — EU AI Act Compliant Stack Demo

Rolling log of what was delivered each day, with token accounting and final state.

---

## Day 1 — 2026-05-12

### Goal
Deliver the explainer documents (Parts 1–3) and the repository scaffolding so subsequent days have a stable home to drop code into.

### Delivered
- `README.md`, `PROGRESS.md`, `manifest.json`
- `docs/01-eu-ai-act-overview.md` — Part 1
- `docs/02-service-provider-implications.md` — Part 2
- `docs/03-operational-aspects.md` — Part 3
- Empty placeholder directories for `backend/`, `frontend/`, `traditional-stack/`, `i18n/`, `tests/`

### Token accounting
- Estimated: ~28,000 tokens (input + output)
- Actual: roughly in line with estimate

---

## Day 2 — 2026-05-13

### Goal
Deliver Part 4: the compliant backend, the traditional baseline for contrast, the React frontend with side-by-side comparison, docker-compose, and the architecture narrative.

### Delivered
**Backend (compliant)** — `backend/`
- FastAPI app with 8 compliance modules (Art. 8–15 + Annex IV docgen).
- Provider-agnostic LLM client with deterministic stub fallback.
- Typed CV/job parser as the prompt-injection defence layer.
- Orchestrated screening endpoint emitting a compliance envelope.

**Traditional baseline** — `traditional-stack/`
- Minimal FastAPI app, same API surface, no controls.

**Frontend** — `frontend/`
- React + Vite UI rendering both stacks side by side.
- ComplianceSidecar with Article 12/13/14/15 evidence surfaces.

**Composition + docs**
- `docker-compose.yml` (backend + traditional + frontend).
- `docs/04-architecture.md`.

### Token accounting
- Estimated: ~79,500 tokens (input + output)
- Actual: in line with estimate

---

## Day 3 — 2026-05-14

### Goal
Deliver Part 5: i18n framework, seed locales for EN/DE/FR/ES/IT, runtime locale-patch CLI, smoke tests, compliance-conformance test suite, end-to-end run guide, and final pass on top-level docs.

### Delivered
**i18n framework**
- `i18n/loader.py` — backend locale loader, hot-reloadable.
- `i18n/locales/en.json`, `de.json`, `fr.json`, `es.json`, `it.json` — seed locales covering UI strings, panel copy, compliance sidecar text, and the Article 50 candidate-disclosure copy.
- `i18n/patch_locale.py` — CLI with `list / show / create / set / unset / validate / reload` subcommands.
- `i18n/README.md` — usage notes + translation-review checklist.
- `backend/app/api/i18n_routes.py` — `GET /i18n/locales`, `GET /i18n/locales/{locale}`, `POST /i18n/reload`.
- Locale-aware `GET /compliance/candidate-disclosure` (Accept-Language + ?lang= query).

**Frontend i18n integration**
- `frontend/src/i18n/I18nProvider.jsx` — context provider hydrating from backend.
- `frontend/src/i18n/LanguageSwitcher.jsx` — language picker.
- All panel components refactored to use `useI18n().t(...)`.

**Docker / cross-cutting**
- Backend Dockerfile and docker-compose updated to mount the repo-root `i18n/` volume read-only into the backend container, enabling hot-reload of locale files without rebuilding.

**Tests**
- `tests/conftest.py` — TestClient + temp-DB fixtures.
- `tests/test_smoke.py` — API surface coverage.
- `tests/test_compliance.py` — one focused test per Article 8–15 control + Article 50 disclosure localisation.
- `tests/README.md` — how to run.

**Docs**
- `docs/05-running-the-demo.md` — end-to-end run guide, 15-minute customer-demo script, i18n patching workflow, test-suite instructions, troubleshooting.
- Final pass on `README.md` to reflect completed state.
- Final pass on `manifest.json`.

### Verification performed in-session
- All Python files compile (`py_compile`).
- All 5 locale JSON files parse and round-trip through the loader.
- `parse_accept_language` resolves `de-DE,en;q=0.8 → de` and `xx-YY → en` correctly.
- `patch_locale.py list / validate / create / set` lifecycle exercised end-to-end against a temporary `nl` locale (then cleaned up).

### Token accounting
- Estimated: ~50,000 tokens (input + output)
- Actual: in line with estimate

---

## Final state

57+ files. Three runnable services. Five seed locales. Two test suites. Five docs.

Total token consumption across all three days: ~155k against a daily working ceiling of 240k. Well within Pro plan headroom.

The project is complete and ready for customer demos.
