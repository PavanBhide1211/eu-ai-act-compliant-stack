# Part 4 — Architecture of the compliant AI stack

> *Audience: engineering and architecture leads, integrators evaluating the demo, and reviewers who want to understand exactly which line of code maps to which Article.*

This document walks through the demo codebase delivered on Day 2. It is structured to answer four questions: what the system does, how it differs from a traditional stack, where each EU AI Act obligation lives in the code, and how to run and exercise the demo locally.

## What the system does

The demo implements **AI-assisted CV screening**, a high-risk use case under Annex III, point 4(a) of Regulation (EU) 2024/1689. A client (the frontend in this repo, or any HTTP client) posts a structured candidate CV and a structured job description to `/screening/score`. Two backends are running:

The **compliant backend** (`backend/`, port 8000) is a FastAPI application that returns a typed recommendation — `shortlist`, `borderline`, or `reject` — together with a score, a confidence, a human-readable explanation, a request ID, and a **compliance envelope** describing the controls that were applied to produce that recommendation. The same backend exposes a parallel `/compliance/...` surface that lets a reviewer or an auditor inspect the intended purpose, the risk register, the data lineage, the chained event log, the model card, the bias monitor, and the Annex IV technical-documentation pack.

The **traditional backend** (`traditional-stack/`, port 8001) is a deliberately minimal FastAPI application with exactly the same scoring math, exactly the same input/output shape, and **none** of the controls. It is included so the difference between "AI that ships today" and "AI that ships under the EU AI Act" is visible side by side, not described in abstract.

The **frontend** (`frontend/`, port 5173) is a React + Vite single-page UI. The top half renders the two stacks' outputs side by side. The bottom half — the **ComplianceSidecar** — surfaces the audit log, the model card, the oversight controls, and the bias monitor in real time, tied to the most recent compliant decision. This is the surface a reviewer, a deployer's auditor, or a national market-surveillance authority would use.

## How it differs from a traditional stack

A traditional AI stack treats the model as the system. The compliant stack treats the model as **one component of** a larger lifecycle whose other components — data governance, risk management, human oversight, transparency, audit, monitoring — are first-class regulated artefacts.

The table below summarises the structural delta as it appears in the code.

| Concern | Traditional stack | Compliant stack | Article |
|---|---|---|---|
| Intended purpose | Not declared, drifts implicitly with deployment. | `system_intended_purpose.yaml`, loaded at boot, change-control gate exposed via API. | Art. 8 |
| Risk register | Not maintained, or maintained in a separate document nobody reads. | `compliance/risk_register.py` seeded with concrete risks; queryable at `/compliance/risk-register`. | Art. 9 |
| Data governance | Implicit. Training data lineage often lost. | `compliance/data_lineage.py` with explicit provenance, transformations, bias-examination summary. | Art. 10 |
| Technical documentation | Not produced, or produced as a static one-off. | `compliance/docgen.py` emits an Annex IV-shaped pack from the live store. | Art. 11 + Annex IV |
| Automatic event logging | Application logs only; lost on retention rollover. | `compliance/audit_log.py` append-only, chained-hash, tamper-evident store; `/compliance/audit-log/verify` confirms integrity. | Art. 12 |
| Transparency to deployers | Marketing copy. | `compliance/model_card.py` generates JSON + markdown card from live state; published at `/compliance/model-card`. | Art. 13 |
| Human oversight | Optional UI affordance, no enforcement. | `compliance/oversight.py` enforces rationale-required intervention with two-person rule; `/compliance/oversight` endpoint. | Art. 14 |
| Accuracy / bias monitoring | Ad-hoc dashboards. | `compliance/bias_monitor.py` computes subgroup parity continuously, raises alerts above threshold. | Art. 15 + Art. 72 |
| Input handling | Raw text to model. | Structured-extracted to typed schema first; raw text never reaches the model. | Art. 15 (robustness) |
| Personal data in logs | Raw PII often logged. | Inputs fingerprinted (`fingerprint()` in `services/llm_client.py`); only hashes reach the audit log. | GDPR + Art. 10(5) |
| Candidate transparency | None. | `/compliance/candidate-disclosure` exposes Art. 50 disclosure copy for the deployer to use. | Art. 50 |
| Conformity-assessment artefacts | Not produced. | Annex IV pack at `/compliance/technical-documentation.md` assembled from live data. | Art. 43 + Annex IV |
| Operational role of the model | The system. | One component, replaceable; controls do not depend on which provider supplies the model. | (architecture) |

The compliant pattern is not "more code" so much as a different shape: the controls are wired around every model call, not glued on afterwards. The traditional stack is roughly 70 lines of code. The compliant stack is roughly 1,400. About 90% of that delta is the controls — exactly the work the Act expects to exist.

## Where each obligation lives in the code

For reviewers tracing obligations to implementation, here is the map.

`backend/app/system_intended_purpose.yaml` — Article 8 declared intended purpose. Loaded at boot, version-controlled, exposed at `/compliance/intended-purpose`.

`backend/app/compliance/intended_purpose.py` — Article 8 boot-time validation and change-control gate. Refuses to boot if the YAML is missing or declares the system as prohibited under Article 5.

`backend/app/compliance/risk_register.py` — Article 9 risk-management system. Seeded with six concrete risks for the CV-screening use case (direct discrimination, feedback loops, automation bias, prompt injection, drift, transparency-to-candidate).

`backend/app/compliance/data_lineage.py` — Article 10 data governance. Provenance, licence basis, transformations, and bias-examination summary for each dataset.

`backend/app/compliance/audit_log.py` — Article 12 automatic event logging. Chained-hash, append-only, tamper-evident. `verify_chain()` replays the chain and confirms integrity.

`backend/app/compliance/model_card.py` — Article 13 transparency to deployers. Generates the card from the live intended-purpose + risk + lineage state. Available as JSON and markdown.

`backend/app/compliance/oversight.py` — Article 14 human oversight. Three actions (accept / override / do_not_use), rationale required, two-person review enforced.

`backend/app/compliance/bias_monitor.py` — Article 15 + Article 72 accuracy / robustness / post-market monitoring. Computes subgroup selection-rate deltas, raises alerts above threshold, writes the alert into the audit log.

`backend/app/compliance/docgen.py` — Article 11 + Annex IV technical-documentation pack generator.

`backend/app/services/llm_client.py` — model layer with **stub-by-default** so the demo runs without API keys, switchable to a real provider via LiteLLM. Output schema constrained to defend against unstructured generations and prompt injection.

`backend/app/services/cv_parser.py` — typed extraction of CV and job description. The defence against prompt injection lives here: the model never sees raw free-form text, only the typed view.

`backend/app/api/screening.py` — the orchestration. The eight-step compliant path (intended-purpose check → pseudonymise → model call → persist decision → audit event → bias refresh → response with compliance envelope) is sequenced here.

`backend/app/api/compliance_routes.py` — the read surface that auditors, reviewers, deployers, and the frontend use to inspect controls and evidence.

`frontend/src/components/ComplianceSidecar.jsx` — the UI surface for the Article 12, 13, 14, and 15/72 evidence; rendered next to the decision so the reviewer can act with the evidence in view.

`frontend/src/components/CompliantPanel.jsx` vs. `frontend/src/components/TraditionalPanel.jsx` — the side-by-side rendering that makes the gap obvious to a non-technical viewer.

## The orchestration on a single request

The compliant `/screening/score` request executes these steps in order, every time:

1. **Validate** input against the typed schema. Reject anything that does not parse.
2. **Intended-purpose check** — assert the deployer and the locale fall inside the declared scope of the system. (In the demo this is lenient; production would consult a contractual-scope register.)
3. **Pseudonymise** the inputs. Compute SHA-256 fingerprints of the CV and job description; only the fingerprints are written to the compliance database. Compute a pseudonymised **bias cohort** for monitoring (locale + experience band).
4. **Call the model.** Inputs are typed; outputs are constrained to a typed schema (`score`, `confidence`, `explanation`). The default stub is deterministic and explainable; switching to a real LLM keeps the same output schema.
5. **Persist the decision row** with the recommendation, score, confidence, explanation, model version, and pseudonymised refs.
6. **Write an Article 12 audit event** — chained-hash, append-only — referencing the decision, the actor, the deployer, and the model version.
7. **Refresh bias metrics.** Selection-rate deltas across cohorts are recomputed; alerts above the threshold are persisted and themselves audit-logged.
8. **Return** the decision plus a **compliance envelope** describing which controls were applied. The envelope is what the frontend renders next to the recommendation so the reviewer can see, at the moment of decision, the evidence they would need in order to override.

## The orchestration on an oversight intervention

When a reviewer submits an oversight action via `/compliance/oversight`:

1. The action is validated. Rationale shorter than 10 characters is rejected — Article 14 expects *meaningful* oversight.
2. The two-person rule is enforced. If the same reviewer has already acted on this decision, the action is refused.
3. The `OversightAction` row is persisted with reviewer, action, optional override, and rationale.
4. The `Decision.oversight_status` is updated; on `override`, the recommendation is replaced.
5. An Article 12 audit event records the intervention.
6. The reviewer receives confirmation; the audit log surface reflects the new event immediately.

## How the controls survive a model swap

A real production system will swap the model — a fine-tune, a new provider, a new vendor model — at least once a year. The compliant pattern keeps the controls intact across swaps because they do not live inside the model; they live around it.

To replace the model, set `LITELLM_PROVIDER` and `LITELLM_MODEL` to the new provider/model. The `LLMClient` wrapper enforces the same typed output schema regardless of provider. The audit log, the bias monitor, the model card, the technical documentation pack, the oversight surface, and the candidate disclosure are unaffected. The only artefacts that **must** change with a model swap are the model card's `model_version`, the declared accuracy (re-evaluated on the held-out set), and a new entry in the change log (Annex IV §5) — all of which are version-controlled artefacts intended to change with the model.

This separation is the deeper architectural point of the compliant pattern: **the regulated artefacts are independent of the model**.

## Running the demo

Prerequisites: Docker Desktop or an equivalent docker-compose runtime.

```bash
# from the repo root
docker compose up --build
```

This will build and start three containers:

- `compliant-backend` on port 8000 (FastAPI, OpenAPI at /docs)
- `traditional-backend` on port 8001 (FastAPI, OpenAPI at /docs)
- `compliant-frontend` on port 5173 (Vite dev server)

Open http://localhost:5173. Pick a job and a candidate from the dropdowns, click "Run both stacks", and the two backends will return their answers. The compliant backend's response will be accompanied by the ComplianceSidecar with live audit log, model card, oversight controls, and bias monitor.

To exercise the controls:

- **Record an oversight action.** Open the Oversight tab; set the reviewer ID, pick an action, type a rationale of at least ten characters, click "Record oversight action". Watch the audit log gain a new entry. Try the same action again with the same reviewer — the two-person rule should reject it.
- **Inspect the audit chain.** Open the Audit tab. The "Chain verification" header should read OK. Drop a row directly in the database (`compliance_events`), reload, and the verification will report BROKEN at the affected ID.
- **Inspect the model card.** Open the Model card tab. The card is regenerated from the live state on every fetch.
- **Trigger a bias alert.** Run several Candidate C (weak match, locale en) and several Candidate A (strong match, locale de) requests; click "Recompute now" in the Bias tab. The selection-rate delta should breach the 0.10 threshold and an alert should appear. The audit log will record the alert under `bias_alert`.
- **Pull the Annex IV pack.** Open `http://localhost:8000/compliance/technical-documentation.md` in a new tab. The pack is assembled from the same live state.

## Running without Docker

If you prefer to run the services directly:

```bash
# compliant backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --port 8000

# traditional baseline (separate terminal)
cd traditional-stack
pip install -r requirements.txt
uvicorn app:app --port 8001

# frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Same UX as the Docker path.

## What's coming on Day 3

Day 3 adds multilingual support across the frontend and the candidate-disclosure surface, with seed locales for English, German, French, Spanish, and Italian, plus a `patch_locale.py` CLI for adding or updating a locale at runtime — no rebuild or redeploy required. Day 3 also adds a smoke-test suite and a small compliance-conformance test suite that verifies each Article 8–15 control is wired and produces evidence on demand.
