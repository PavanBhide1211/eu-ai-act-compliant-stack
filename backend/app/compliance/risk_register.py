"""Article 9 — Risk-management system.

Seeded with the risks that an Annex III point 4(a) CV-screening system would
ordinarily carry. The register is queryable from the API and feeds the
Annex IV technical documentation generator.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models import RiskRegisterEntry


SEED_RISKS = [
    {
        "risk_id": "R-001",
        "title": "Direct discrimination by protected attribute",
        "description": (
            "The model could learn proxies for protected attributes (e.g. name, "
            "address, university) and produce systematically lower scores for "
            "candidates from protected groups."
        ),
        "category": "fundamental_rights",
        "severity": "high",
        "likelihood": "medium",
        "mitigations": [
            "Sensitive-attribute features explicitly excluded from input.",
            "Bias monitor computes subgroup selection-rate deltas and alerts.",
            "Quarterly fairness audit by independent reviewer.",
        ],
        "residual_risk": "medium",
    },
    {
        "risk_id": "R-002",
        "title": "Self-reinforcing feedback loop",
        "description": (
            "Outputs that are accepted by recruiters feed back into hiring "
            "outcomes and could be used to retrain the model, amplifying any "
            "initial bias."
        ),
        "category": "model_quality",
        "severity": "high",
        "likelihood": "medium",
        "mitigations": [
            "Retraining data set must include human-overridden cases with the "
            "overridden label, not the model's original label.",
            "Periodic counterfactual evaluation against held-out cohorts.",
        ],
        "residual_risk": "medium",
    },
    {
        "risk_id": "R-003",
        "title": "Over-reliance / automation bias",
        "description": (
            "Recruiters defer to the recommendation without meaningful review, "
            "rendering the human oversight nominal."
        ),
        "category": "human_oversight",
        "severity": "high",
        "likelihood": "high",
        "mitigations": [
            "UX requires reviewer to enter rationale on accept and on override.",
            "Two-person review for shortlists over threshold or close-margin cases.",
            "Monthly oversight intervention-rate report; floors agreed with "
            "deployer; falling below floor triggers retraining of reviewers.",
        ],
        "residual_risk": "medium",
    },
    {
        "risk_id": "R-004",
        "title": "Prompt injection / adversarial CV",
        "description": (
            "A candidate embeds instructions in the CV designed to manipulate "
            "the model's output."
        ),
        "category": "robustness_security",
        "severity": "medium",
        "likelihood": "medium",
        "mitigations": [
            "Input is structured-extracted before prompting; raw text is not "
            "passed verbatim to the model.",
            "Output is constrained to a typed schema; free-form deviations are "
            "rejected.",
            "Adversarial test suite runs in CI.",
        ],
        "residual_risk": "low",
    },
    {
        "risk_id": "R-005",
        "title": "Drift in candidate population",
        "description": (
            "The candidate pool shifts (new geography, new role family, new "
            "language) outside the training distribution, accuracy degrades."
        ),
        "category": "post_market_monitoring",
        "severity": "medium",
        "likelihood": "high",
        "mitigations": [
            "Input-distribution drift detector; alert on KL-divergence beyond "
            "threshold.",
            "Per-locale and per-role accuracy tracked in monitoring dashboard.",
            "Defined retraining cadence on drift breach.",
        ],
        "residual_risk": "medium",
    },
    {
        "risk_id": "R-006",
        "title": "Insufficient transparency to candidate",
        "description": (
            "Candidates affected by the recommendation are not informed of "
            "the AI's role or their right to human review."
        ),
        "category": "transparency",
        "severity": "high",
        "likelihood": "low",
        "mitigations": [
            "Deployer contract requires candidate-facing disclosure.",
            "Reference disclosure copy is shipped in docs/04-architecture.md.",
        ],
        "residual_risk": "low",
    },
]


def seed_if_empty(s: Session) -> None:
    """Populate the risk register on first boot if empty."""
    if s.query(RiskRegisterEntry).count():
        return
    now = datetime.now(timezone.utc)
    for r in SEED_RISKS:
        s.add(
            RiskRegisterEntry(
                **r, last_reviewed=now, reviewer="initial_seed@compliance"
            )
        )
    s.commit()


def list_risks(s: Session) -> list[dict]:
    rows = s.query(RiskRegisterEntry).order_by(RiskRegisterEntry.risk_id).all()
    return [
        {
            "risk_id": r.risk_id,
            "title": r.title,
            "description": r.description,
            "category": r.category,
            "severity": r.severity,
            "likelihood": r.likelihood,
            "mitigations": r.mitigations,
            "residual_risk": r.residual_risk,
            "last_reviewed": r.last_reviewed.isoformat(),
            "reviewer": r.reviewer,
        }
        for r in rows
    ]
