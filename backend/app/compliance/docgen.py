"""Article 11 + Annex IV — Technical documentation pack generator.

Assembles a single markdown document covering each Annex IV heading by pulling
from the live compliance store. The same generator can render to PDF in a
production deployment by piping markdown -> wkhtmltopdf or similar.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.config import settings
from app.compliance import (
    intended_purpose,
    risk_register,
    data_lineage,
    audit_log,
    model_card,
    bias_monitor,
)


ANNEX_IV_HEADINGS = [
    "1. General description of the AI system",
    "2. Detailed description of elements and development process",
    "3. Information about monitoring, functioning and control",
    "4. Risk-management system",
    "5. Relevant changes through the lifecycle",
    "6. Harmonised standards applied (or technical solutions chosen)",
    "7. EU declaration of conformity",
    "8. Post-market monitoring system",
]


def generate(s: Session) -> str:
    purpose = intended_purpose.load_intended_purpose()
    risks = risk_register.list_risks(s)
    lineage = data_lineage.list_lineage(s)
    chain = audit_log.verify_chain(s)
    bias = bias_monitor.latest_summary(s, limit=10)
    card = model_card.build_model_card(s)

    lines: list[str] = []
    lines.append("# Annex IV — Technical Documentation Pack")
    lines.append("")
    lines.append(
        f"_Generated at {datetime.now(timezone.utc).isoformat()} by the "
        "compliance backend. This pack is a regulatory artefact; treat all "
        "fields as on-the-record._"
    )
    lines.append("")

    # 1. General description
    lines.append(f"## {ANNEX_IV_HEADINGS[0]}")
    lines.append(f"- **System ID:** {purpose['system_id']}")
    lines.append(f"- **Version:** {purpose['version']}")
    lines.append(f"- **Provider:** {purpose.get('provider')}")
    lines.append(f"- **Provider contact:** {purpose.get('provider_contact')}")
    lines.append(f"- **Intended purpose:** {purpose['intended_purpose']}")
    lines.append(
        f"- **Risk classification:** {purpose['risk_classification']['tier']} "
        f"({purpose['risk_classification']['basis']})"
    )
    lines.append("")

    # 2. Development process
    lines.append(f"## {ANNEX_IV_HEADINGS[1]}")
    lines.append("### Datasets")
    for d in lineage:
        lines.append(
            f"- **{d['dataset_id']}** — source: {d['source']}; "
            f"licence: {d['licence_basis']}; transformations: "
            f"{', '.join(d['transformations'])}."
        )
    lines.append("")
    lines.append("### Bias examination summary")
    for d in lineage:
        lines.append(f"- **{d['dataset_id']}**: {d['bias_examination_summary']}")
    lines.append("")

    # 3. Monitoring, functioning and control
    lines.append(f"## {ANNEX_IV_HEADINGS[2]}")
    lines.append("### Declared accuracy")
    for k, v in (purpose.get("declared_accuracy") or {}).items():
        lines.append(f"- **{k}**: {v}")
    lines.append("")
    lines.append("### Human oversight design")
    for x in purpose.get("human_oversight_design", []):
        lines.append(f"- {x}")
    lines.append("")
    lines.append("### Logging")
    lines.append(
        f"- Retention: {settings.audit_log_retention_days} days. Chain "
        f"verification at generation time: {'OK' if chain['ok'] else 'BROKEN'} "
        f"({chain['events']} events)."
    )
    lines.append("")

    # 4. Risk-management system
    lines.append(f"## {ANNEX_IV_HEADINGS[3]}")
    for r in risks:
        lines.append(
            f"### {r['risk_id']} — {r['title']} ({r['category']}, "
            f"severity={r['severity']}, residual={r['residual_risk']})"
        )
        lines.append(r["description"])
        lines.append("**Mitigations:**")
        for m in r["mitigations"]:
            lines.append(f"- {m}")
        lines.append(
            f"_Last reviewed {r['last_reviewed']} by {r['reviewer']}._"
        )
        lines.append("")

    # 5. Relevant changes through lifecycle (stub — would be sourced from a
    # change-log table in production)
    lines.append(f"## {ANNEX_IV_HEADINGS[4]}")
    lines.append(
        "_Source-of-truth: git history of system_intended_purpose.yaml and "
        "the model registry. No substantial change has been registered in "
        "this demo deployment._"
    )
    lines.append("")

    # 6. Standards applied
    lines.append(f"## {ANNEX_IV_HEADINGS[5]}")
    lines.append(
        "- ISO/IEC 42001:2023 (AI management systems) — applied where "
        "applicable."
    )
    lines.append(
        "- ISO/IEC 23894:2023 (AI risk management) — applied to the "
        "risk-management system."
    )
    lines.append(
        "- ISO/IEC 5259-x series (data quality for AI) — applied to the "
        "data-governance procedures."
    )
    lines.append("")

    # 7. EU declaration of conformity
    lines.append(f"## {ANNEX_IV_HEADINGS[6]}")
    lines.append(
        "_For the demo, this is a stub. In a real deployment, the signed "
        "declaration of conformity under Article 47 would be inserted "
        "verbatim, including provider identity, conformity-assessment "
        "procedure followed, and CE-marking date._"
    )
    lines.append("")

    # 8. Post-market monitoring
    lines.append(f"## {ANNEX_IV_HEADINGS[7]}")
    lines.append("### Latest bias-monitoring observations")
    if not bias:
        lines.append("_No metrics yet — no decisions logged._")
    else:
        for m in bias:
            flag = "ALERT" if m["alert"] else "ok"
            lines.append(
                f"- {m['ts']} — {m['metric']} between {m['cohort_a']} and "
                f"{m['cohort_b']}: {m['value']:.4f} (threshold "
                f"{m['threshold']:.2f}) [{flag}]"
            )
    lines.append("")
    lines.append(
        "Serious-incident reporting under Article 73 is integrated with the "
        "deployer's incident-response runbook; reporting deadlines are "
        "tracked from event awareness."
    )
    lines.append("")

    return "\n".join(lines)
