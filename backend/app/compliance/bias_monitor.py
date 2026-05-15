"""Article 15 + Article 72 — Accuracy, robustness, and post-market monitoring.

Computes simple subgroup parity metrics over the live decisions table and
records alerts when the configured threshold is breached.

The bias_cohort attribute on decisions is *not* a protected attribute itself;
it is a pseudonymised bucket (e.g. 'locale_de_band_1') used solely for the
Article 10(5) bias-correction purpose. The raw attribute, if it exists at all,
lives on the application side and never enters this module.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import settings
from app.models import Decision, BiasMetric
from app.compliance import audit_log


SHORTLIST = "shortlist"


def selection_rate_by_cohort(s: Session) -> dict[str, float]:
    """Return shortlist rate per cohort. Cohorts with fewer than 5 decisions are
    excluded — too small to be statistically meaningful and a privacy risk."""
    rows = (
        s.query(
            Decision.bias_cohort,
            func.count(Decision.id).label("n"),
            func.sum(
                func.case((Decision.recommendation == SHORTLIST, 1), else_=0)
            ).label("k"),
        )
        .group_by(Decision.bias_cohort)
        .all()
    )
    out: dict[str, float] = {}
    for cohort, n, k in rows:
        if cohort is None or (n or 0) < 5:
            continue
        out[cohort] = float(k or 0) / float(n)
    return out


def compute_and_record(s: Session) -> dict:
    rates = selection_rate_by_cohort(s)
    metrics: list[dict] = []
    cohorts = sorted(rates)
    alerts: list[dict] = []
    for i, a in enumerate(cohorts):
        for b in cohorts[i + 1 :]:
            delta = abs(rates[a] - rates[b])
            alert = delta > settings.bias_alert_threshold
            m = BiasMetric(
                cohort_a=a,
                cohort_b=b,
                metric="selection_rate_delta",
                value=delta,
                threshold=settings.bias_alert_threshold,
                alert=alert,
            )
            s.add(m)
            metrics.append(
                {
                    "cohort_a": a,
                    "cohort_b": b,
                    "metric": "selection_rate_delta",
                    "value": round(delta, 4),
                    "threshold": settings.bias_alert_threshold,
                    "alert": alert,
                }
            )
            if alert:
                alerts.append(metrics[-1])
    s.commit()

    if alerts:
        audit_log.record(
            s,
            event_type="bias_alert",
            payload={"alerts": alerts, "rates": rates},
            system_version=settings.app_version,
        )

    return {
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "rates": rates,
        "metrics": metrics,
        "alerts": alerts,
        "threshold": settings.bias_alert_threshold,
    }


def latest_summary(s: Session, limit: int = 20) -> list[dict]:
    rows = (
        s.query(BiasMetric)
        .order_by(BiasMetric.ts.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "ts": r.ts.isoformat(),
            "cohort_a": r.cohort_a,
            "cohort_b": r.cohort_b,
            "metric": r.metric,
            "value": r.value,
            "threshold": r.threshold,
            "alert": r.alert,
        }
        for r in rows
    ]
