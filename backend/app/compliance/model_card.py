"""Article 13 — Transparency to deployers.

The model card is generated from the same sources of truth used to operate the
system: the intended purpose, the risk register, the data lineage register, and
the live monitoring metrics. It is intentionally short, structured, and exposed
both as JSON (for API consumers) and as a markdown document (for humans).
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.config import settings
from app.compliance import intended_purpose, risk_register, data_lineage


def build_model_card(s: Session) -> dict:
    purpose = intended_purpose.load_intended_purpose()
    risks = risk_register.list_risks(s)
    lineage = data_lineage.list_lineage(s)
    return {
        "card_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "system": {
            "id": purpose["system_id"],
            "version": purpose["version"],
            "provider": purpose.get("provider"),
            "provider_contact": purpose.get("provider_contact"),
        },
        "intended_purpose": purpose["intended_purpose"],
        "intended_deployers": purpose.get("intended_deployers", []),
        "intended_users": purpose.get("intended_users", []),
        "risk_classification": purpose["risk_classification"],
        "prohibited_uses": purpose.get("prohibited_uses", []),
        "declared_accuracy": purpose.get("declared_accuracy", {}),
        "known_limitations": purpose.get("known_limitations", []),
        "human_oversight_design": purpose.get("human_oversight_design", []),
        "datasets": [
            {
                "id": d["dataset_id"],
                "source": d["source"],
                "licence_basis": d["licence_basis"],
                "bias_examination": d["bias_examination_summary"],
            }
            for d in lineage
        ],
        "risks": [
            {
                "id": r["risk_id"],
                "title": r["title"],
                "residual_risk": r["residual_risk"],
                "mitigations": r["mitigations"],
            }
            for r in risks
        ],
        "logging": {
            "retention_days": settings.audit_log_retention_days,
            "schema_reference": "compliance_events table; see app/models.py",
        },
        "contact_for_redress": purpose.get("provider_contact"),
    }


def render_markdown(card: dict) -> str:
    """Human-readable model card for inclusion in the technical documentation
    pack and for display in the frontend."""
    lines = [
        f"# Model Card — {card['system']['id']} {card['system']['version']}",
        "",
        f"_Generated {card['generated_at']}_",
        "",
        "## Intended purpose",
        card["intended_purpose"],
        "",
        f"**Risk classification:** {card['risk_classification']['tier']} — "
        f"{card['risk_classification']['basis']}",
        "",
        "## Prohibited uses",
        *[f"- {p}" for p in card["prohibited_uses"]],
        "",
        "## Declared accuracy",
        *[f"- **{k}**: {v}" for k, v in card["declared_accuracy"].items()],
        "",
        "## Known limitations",
        *[f"- {x}" for x in card["known_limitations"]],
        "",
        "## Human oversight design",
        *[f"- {x}" for x in card["human_oversight_design"]],
        "",
        "## Datasets",
        *[
            f"- **{d['id']}** — {d['source']} (licence: {d['licence_basis']}). "
            f"Bias examination: {d['bias_examination']}"
            for d in card["datasets"]
        ],
        "",
        "## Key risks and residual exposure",
        *[
            f"- **{r['id']} — {r['title']}** (residual: {r['residual_risk']})"
            for r in card["risks"]
        ],
        "",
        "## Logging",
        f"- Retention: {card['logging']['retention_days']} days",
        f"- Schema: {card['logging']['schema_reference']}",
        "",
        "## Contact for redress",
        card.get("contact_for_redress") or "(provider contact missing)",
    ]
    return "\n".join(lines)
