"""Compliance-facing API surface.

Every artefact the Act expects the provider to be able to produce on request
is exposed here. The frontend's ComplianceSidecar consumes these endpoints.
"""

import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_session
from app.compliance import (
    intended_purpose,
    risk_register,
    data_lineage,
    audit_log,
    model_card,
    oversight,
    bias_monitor,
    docgen,
)

# Locale loader from the i18n package — robust to Docker vs. local layouts.
def _ensure_i18n_importable() -> None:
    here = Path(__file__).resolve()
    for cand in [here.parents[2], here.parents[3]]:
        if (cand / "i18n" / "loader.py").exists():
            if str(cand) not in sys.path:
                sys.path.insert(0, str(cand))
            return


_ensure_i18n_importable()
from i18n import loader as i18n_loader  # noqa: E402


router = APIRouter(prefix="/compliance", tags=["compliance"])


# ---------- Article 8: intended purpose
@router.get("/intended-purpose")
def get_intended_purpose() -> dict:
    return intended_purpose.load_intended_purpose()


# ---------- Article 9: risk register
@router.get("/risk-register")
def get_risks(s: Session = Depends(get_session)) -> list[dict]:
    return risk_register.list_risks(s)


# ---------- Article 10: data lineage
@router.get("/data-lineage")
def get_lineage(s: Session = Depends(get_session)) -> list[dict]:
    return data_lineage.list_lineage(s)


# ---------- Article 12: audit log
@router.get("/audit-log")
def get_audit_log(
    s: Session = Depends(get_session),
    limit: int = 100,
    event_type: Optional[str] = None,
    request_id: Optional[str] = None,
) -> dict:
    return {
        "verification": audit_log.verify_chain(s),
        "events": audit_log.fetch(
            s, limit=limit, event_type=event_type, request_id=request_id
        ),
    }


@router.post("/audit-log/verify")
def verify_audit_chain(s: Session = Depends(get_session)) -> dict:
    return audit_log.verify_chain(s)


# ---------- Article 13: model card
@router.get("/model-card")
def get_model_card(s: Session = Depends(get_session)) -> dict:
    return model_card.build_model_card(s)


@router.get("/model-card.md", response_class=PlainTextResponse)
def get_model_card_md(s: Session = Depends(get_session)) -> str:
    return model_card.render_markdown(model_card.build_model_card(s))


# ---------- Article 14: human oversight
class OversightRequest(BaseModel):
    request_id: str
    reviewer_id: str
    action: str  # accept / override / do_not_use
    overridden_recommendation: Optional[str] = None
    rationale: str


@router.post("/oversight")
def post_oversight(
    body: OversightRequest, s: Session = Depends(get_session)
) -> dict:
    try:
        return oversight.record_action(
            s,
            request_id=body.request_id,
            reviewer_id=body.reviewer_id,
            action=body.action,
            overridden_recommendation=body.overridden_recommendation,
            rationale=body.rationale,
        )
    except oversight.OversightError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/oversight/{request_id}")
def get_oversight(
    request_id: str, s: Session = Depends(get_session)
) -> list[dict]:
    return oversight.list_actions_for(s, request_id)


# ---------- Article 15 / 72: bias monitoring
@router.get("/bias-monitor")
def get_bias_monitor(s: Session = Depends(get_session)) -> dict:
    return {
        "rates": bias_monitor.selection_rate_by_cohort(s),
        "recent_metrics": bias_monitor.latest_summary(s),
    }


@router.post("/bias-monitor/recompute")
def recompute_bias(s: Session = Depends(get_session)) -> dict:
    return bias_monitor.compute_and_record(s)


# ---------- Article 11 / Annex IV: technical documentation pack
@router.get("/technical-documentation.md", response_class=PlainTextResponse)
def get_tech_docs(s: Session = Depends(get_session)) -> str:
    return docgen.generate(s)


# ---------- Article 50: candidate-facing transparency text (locale-aware)
@router.get("/candidate-disclosure", response_class=PlainTextResponse)
def candidate_disclosure(
    lang: Optional[str] = Query(default=None),
    accept_language: Optional[str] = Header(default=None),
) -> str:
    """Return the Article 50 disclosure copy in the requested locale.

    Resolution order: explicit ?lang= query param -> Accept-Language header
    -> English fallback. Any unknown locale falls back to English.
    """
    locale = lang or i18n_loader.parse_accept_language(accept_language)
    return i18n_loader.t(
        "disclosure.candidate",
        locale=locale,
        default=(
            "You are being assessed with the assistance of an AI system. The "
            "AI produces a recommendation only; every hiring decision is made "
            "by a human recruiter. You have the right to request a human "
            "review of any AI-assisted assessment and to contest the outcome."
        ),
    )
