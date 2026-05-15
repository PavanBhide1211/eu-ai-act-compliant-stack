"""Primary screening endpoint. This is the surface compared against the
traditional baseline.

The compliant path:
  1. Validate input against typed schema (defence against prompt injection).
  2. Verify intended-purpose scope (Article 8).
  3. Compute pseudonymised bias cohort (Article 10(5) safeguarded).
  4. Call the model layer (constrained schema).
  5. Persist Decision row.
  6. Write Article 12 audit event with fingerprinted refs.
  7. Recompute subgroup bias metrics (Article 15 / 72).
  8. Return decision + a `compliance_envelope` describing the controls applied.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_session
from app.models import Decision
from app.services.cv_parser import ScreeningRequest, derive_bias_cohort
from app.services.llm_client import (
    LLMClient,
    fingerprint,
    recommendation_for_score,
)
from app.compliance import (
    intended_purpose,
    audit_log,
    bias_monitor,
)


router = APIRouter(prefix="/screening", tags=["screening"])


@router.post("/score")
def score(req: ScreeningRequest, s: Session = Depends(get_session)) -> dict:
    # 1. Intended-purpose check
    intended_purpose.assert_use_within_purpose(
        deployer_id=req.deployer_id,
        deployer_geography=req.cv.locale,
    )

    # 2. Pseudonymise inputs
    candidate_ref = fingerprint(req.cv.model_dump())
    job_ref = fingerprint(req.job.model_dump())
    request_id = uuid.uuid4().hex
    bias_cohort = derive_bias_cohort(req.cv)

    # 3. Model call
    client = LLMClient()
    result = client.score_cv(cv=req.cv.model_dump(), job=req.job.model_dump())
    recommendation = recommendation_for_score(result["score"])

    # 4. Persist decision
    decision = Decision(
        request_id=request_id,
        candidate_ref=candidate_ref,
        job_ref=job_ref,
        recommendation=recommendation,
        score=result["score"],
        confidence=result["confidence"],
        explanation=result["explanation"],
        model_version=result["model_version"],
        bias_cohort=bias_cohort,
        oversight_status="pending",
    )
    s.add(decision)
    s.commit()

    # 5. Audit event
    audit_log.record(
        s,
        event_type="screening_decision",
        payload={
            "request_id": request_id,
            "candidate_ref": candidate_ref,
            "job_ref": job_ref,
            "recommendation": recommendation,
            "score": result["score"],
            "confidence": result["confidence"],
            "bias_cohort": bias_cohort,
        },
        system_version=settings.app_version,
        model_version=result["model_version"],
        deployer_id=req.deployer_id,
        actor_id=req.requested_by_user,
        subject_ref=candidate_ref,
    )

    # 6. Refresh bias metrics
    bias_snapshot = bias_monitor.compute_and_record(s)

    return {
        "request_id": request_id,
        "recommendation": recommendation,
        "score": result["score"],
        "confidence": result["confidence"],
        "explanation": result["explanation"],
        "model_version": result["model_version"],
        "oversight_status": "pending",
        "compliance_envelope": {
            "intended_purpose_checked": True,
            "input_pseudonymised": True,
            "audit_event_written": True,
            "bias_metrics_refreshed": True,
            "bias_alerts": bias_snapshot["alerts"],
            "two_person_oversight_required": settings.require_two_person_oversight,
            "candidate_ref": candidate_ref,
            "bias_cohort": bias_cohort,
        },
    }


@router.get("/decisions/{request_id}")
def get_decision(request_id: str, s: Session = Depends(get_session)) -> dict:
    d = s.query(Decision).filter(Decision.request_id == request_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="decision not found")
    return {
        "request_id": d.request_id,
        "ts": d.ts.isoformat(),
        "recommendation": d.recommendation,
        "score": d.score,
        "confidence": d.confidence,
        "explanation": d.explanation,
        "model_version": d.model_version,
        "oversight_status": d.oversight_status,
        "bias_cohort": d.bias_cohort,
    }
