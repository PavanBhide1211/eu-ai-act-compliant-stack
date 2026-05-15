# EU AI Act Compliant AI Stack — Demo

A reference implementation of an AI application stack designed from the ground up to satisfy the obligations of **Regulation (EU) 2024/1689 — the EU Artificial Intelligence Act**. The demo intentionally ships alongside a "traditional" AI stack of equivalent functionality so customers can see, side by side, what compliance actually adds in code, controls, and operations.

## Status

**Complete.** Built over three days; all five scoped parts delivered.

| Part | Scope | Delivered |
|---|---|---|
| 1 | What is the EU AI Act? Business impact in the EU. | `docs/01-eu-ai-act-overview.md` |
| 2 | Implications for service providers and data handlers. | `docs/02-service-provider-implications.md` |
| 3 | Critical operational aspects for daily business. | `docs/03-operational-aspects.md` |
| 4 | Compliant codebase, contrasted with a traditional baseline. | `backend/`, `traditional-stack/`, `frontend/`, `docs/04-architecture.md` |
| 5 | Multilingual support with pluggable language patching. | `i18n/` + `i18n/patch_locale.py` + 5 seed locales |

## Demo use case

An **AI-assisted CV screening assistant** — a textbook **high-risk AI system** under Annex III of the EU AI Act (employment, workers management and access to self-employment, point 4(a)).

The system ingests candidate CVs and a job description, scores candidate–role fit, and produces a shortlist for a human recruiter. Two parallel implementations are provided:

- `traditional-stack/` — the way most teams ship this today: call the model, return a score.
- `backend/` + `frontend/` — the compliant version: the same functional output, surrounded by the risk-management, data-governance, transparency, human-oversight, audit, monitoring, and post-market-incident controls the Act requires.

## Quick start

```bash
docker compose up --build
```

Then open `http://localhost:5173`.

Full run guide, customer-demo script, i18n patching workflow, and test instructions live in [`docs/05-running-the-demo.md`](docs/05-running-the-demo.md).

## Repository layout

```
eu-ai-act-compliant-stack/
├── README.md                      # this file
├── PROGRESS.md                    # rolling delivery log
├── manifest.json                  # machine-readable progress + scope tracker
├── docker-compose.yml             # one-command spin-up
├── docs/
│   ├── 01-eu-ai-act-overview.md
│   ├── 02-service-provider-implications.md
│   ├── 03-operational-aspects.md
│   ├── 04-architecture.md
│   └── 05-running-the-demo.md
├── backend/                       # FastAPI compliant stack
│   ├── app/
│   │   ├── compliance/            # 8 modules, one per Art. 8-15 control
│   │   ├── api/                   # screening + compliance + i18n routes
│   │   ├── services/              # LLM client (stub-by-default), CV parser
│   │   └── system_intended_purpose.yaml
│   └── ...
├── traditional-stack/             # the baseline (no controls)
├── frontend/                      # React + Vite UI with side-by-side panels
│   └── src/
│       ├── i18n/                  # locale provider + language switcher
│       └── components/            # panels, sidecar, oversight, audit, etc.
├── i18n/                          # locale framework
│   ├── loader.py                  # backend locale loader
│   ├── patch_locale.py            # runtime locale-management CLI
│   └── locales/                   # en, de, fr, es, it
└── tests/                         # smoke + compliance-conformance tests
```

## Obligation → code map

For reviewers tracing obligations to implementation:

| Article | Implementation |
|---|---|
| Art. 8 — Intended purpose | `backend/app/system_intended_purpose.yaml` + `backend/app/compliance/intended_purpose.py` |
| Art. 9 — Risk-management system | `backend/app/compliance/risk_register.py` |
| Art. 10 — Data governance | `backend/app/compliance/data_lineage.py` |
| Art. 11 + Annex IV — Tech documentation | `backend/app/compliance/docgen.py` |
| Art. 12 — Automatic event logging | `backend/app/compliance/audit_log.py` (chained-hash, append-only) |
| Art. 13 — Transparency to deployers | `backend/app/compliance/model_card.py` |
| Art. 14 — Human oversight | `backend/app/compliance/oversight.py` (rationale required, two-person rule) |
| Art. 15 + 72 — Accuracy / robustness / monitoring | `backend/app/compliance/bias_monitor.py` |
| Art. 50 — Candidate-facing transparency | `backend/app/api/compliance_routes.py` (locale-aware) |

## Tech stack

- **Backend**: Python 3.11 + FastAPI
- **Frontend**: React 18 + Vite
- **Storage**: SQLite (separate compliance store; production target: Postgres)
- **Model layer**: LiteLLM — provider-agnostic, defaults to a deterministic stub so the demo runs without API keys
- **i18n**: JSON locale files + small loader, hot-reloadable via CLI
- **Containerisation**: Docker Compose

## License and disclaimer

This is a **demonstration codebase**. It is intended to illustrate how the obligations of the EU AI Act can be operationalized in software. It is **not legal advice**, it is **not a certified conformity assessment**, and it must not be deployed in production for a real high-risk AI system without (a) a proper Article 43 conformity assessment, (b) registration in the EU database under Article 71, and (c) sign-off from your legal and compliance functions.

The seed translations under `i18n/locales/` have not been reviewed by professional linguists or legal counsel; production deployments must do so. See `i18n/README.md` and `docs/05-running-the-demo.md` for the translation review checklist.

References to specific Articles, Annexes, and dates in this repo are based on the final adopted text of Regulation (EU) 2024/1689 and the European Commission's implementation timeline as published.
