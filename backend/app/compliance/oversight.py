"""Article 14 — Human oversight.

Three controls are exposed to the frontend and to API consumers:

  accept          — reviewer signs off on the recommendation as-is. Rationale required.
  override        — reviewer changes the recommendation. Old and new recorded,
                    rationale required.
  do_not_use      — reviewer marks the AI recommendation as not to be relied on
                    for this case. Rationale required.

Two-person review is enforced when the demo policy flag is set; one of the
reviewers must be distinct from the user who first viewed the recommendation.
"""

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Decision, OversightAction
from app.compliance import audit_log


VALID_ACTIONS = {"accept", "override", "do_not_use"}


class OversightError(Exception):
    pass


def record_action(
    s: Session,
    *,
    request_id: str,
    reviewer_id: str,
    action: str,
    overridden_recommendation: str | None = None,
    rationale: str,
) -> dict:
    if action not in VALID_ACTIONS:
        raise OversightError(f"action must be one of {sorted(VALID_ACTIONS)}")
    if not rationale or len(rationale.strip()) < 10:
        raise OversightError(
            "rationale is required and must be at least 10 characters. "
            "Article 14 requires *meaningful* oversight — boilerplate is not "
            "meaningful."
        )

    decision = (
        s.query(Decision).filter(Decision.request_id == request_id).first()
    )
    if not decision:
        raise OversightError(f"no decision for request_id={request_id}")

    if action == "override" and not overridden_recommendation:
        raise OversightError("overridden_recommendation required for action=override")

    # Two-person review enforcement: refuse if same reviewer already acted.
    if settings.require_two_person_oversight:
        prior = (
            s.query(OversightAction)
            .filter(OversightAction.decision_request_id == request_id)
            .all()
        )
        if any(p.reviewer_id == reviewer_id for p in prior):
            raise OversightError(
                "Two-person review required: this reviewer has already acted "
                "on this decision. A different reviewer must take the next "
                "action."
            )

    oa = OversightAction(
        decision_request_id=request_id,
        reviewer_id=reviewer_id,
        action=action,
        overridden_recommendation=overridden_recommendation,
        rationale=rationale,
    )
    s.add(oa)

    decision.oversight_status = {
        "accept": "accepted",
        "override": "overridden",
        "do_not_use": "do_not_use",
    }[action]
    if action == "override":
        decision.recommendation = overridden_recommendation  # type: ignore[assignment]

    s.commit()

    audit_log.record(
        s,
        event_type="oversight_action",
        payload={
            "request_id": request_id,
            "action": action,
            "overridden_recommendation": overridden_recommendation,
            "rationale_length": len(rationale),
        },
        system_version=settings.app_version,
        model_version=decision.model_version,
        actor_id=reviewer_id,
        subject_ref=decision.candidate_ref,
    )

    return {
        "ok": True,
        "request_id": request_id,
        "new_oversight_status": decision.oversight_status,
        "action": action,
    }


def list_actions_for(s: Session, request_id: str) -> list[dict]:
    rows = (
        s.query(OversightAction)
        .filter(OversightAction.decision_request_id == request_id)
        .order_by(OversightAction.ts.asc())
        .all()
    )
    return [
        {
            "ts": r.ts.isoformat(),
            "reviewer_id": r.reviewer_id,
            "action": r.action,
            "overridden_recommendation": r.overridden_recommendation,
            "rationale": r.rationale,
        }
        for r in rows
    ]
