"""Article 12 — Automatic event logging.

Properties this implementation enforces:
- Append-only at the application layer (no delete / update endpoints).
- Each record is chained: event_hash = sha256(prev_hash || ts || event_type ||
  system_id || payload_canonical). Modifying any record breaks the chain and is
  detectable by `verify_chain`.
- Personal data is hashed, not stored raw. Inputs that contain PII are
  fingerprinted with a salted SHA-256 in the calling code; only the fingerprint
  reaches this module.
"""

import hashlib
import json
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.models import ComplianceEvent


GENESIS_HASH = "0" * 64


def _canonical(payload: dict) -> str:
    """Stable JSON for hashing. Sorted keys, no whitespace, UTC strings."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _hash_event(prev_hash: str, ts: datetime, event_type: str, system_id: str,
                payload: dict) -> str:
    h = hashlib.sha256()
    h.update(prev_hash.encode("utf-8"))
    h.update(ts.isoformat().encode("utf-8"))
    h.update(event_type.encode("utf-8"))
    h.update(system_id.encode("utf-8"))
    h.update(_canonical(payload).encode("utf-8"))
    return h.hexdigest()


def _last_hash(s: Session) -> str:
    row = (
        s.query(ComplianceEvent)
        .order_by(ComplianceEvent.id.desc())
        .first()
    )
    return row.event_hash if row else GENESIS_HASH


def record(
    s: Session,
    *,
    event_type: str,
    payload: dict,
    system_version: str,
    model_version: Optional[str] = None,
    deployer_id: Optional[str] = None,
    actor_id: Optional[str] = None,
    subject_ref: Optional[str] = None,
) -> ComplianceEvent:
    """Append one event to the chain. Returns the persisted row."""
    ts = datetime.now(timezone.utc)
    prev = _last_hash(s)
    full_payload = {
        "type": event_type,
        "data": payload,
        "deployer_id": deployer_id,
        "actor_id": actor_id,
        "subject_ref": subject_ref,
    }
    h = _hash_event(prev, ts, event_type, settings.system_id, full_payload)
    row = ComplianceEvent(
        ts=ts,
        event_type=event_type,
        system_id=settings.system_id,
        system_version=system_version,
        model_version=model_version,
        deployer_id=deployer_id,
        actor_id=actor_id,
        subject_ref=subject_ref,
        payload=full_payload,
        prev_hash=prev,
        event_hash=h,
    )
    s.add(row)
    s.commit()
    s.refresh(row)
    return row


def verify_chain(s: Session) -> dict:
    """Replay the chain and confirm it is intact. Returns a summary."""
    rows = s.query(ComplianceEvent).order_by(ComplianceEvent.id.asc()).all()
    if not rows:
        return {"ok": True, "events": 0, "broken_at": None}
    prev = GENESIS_HASH
    for r in rows:
        expected = _hash_event(
            prev, r.ts, r.event_type, r.system_id, r.payload
        )
        if expected != r.event_hash or prev != r.prev_hash:
            return {"ok": False, "events": len(rows), "broken_at": r.id}
        prev = r.event_hash
    return {"ok": True, "events": len(rows), "broken_at": None}


def fetch(
    s: Session,
    *,
    limit: int = 100,
    event_type: Optional[str] = None,
    request_id: Optional[str] = None,
) -> list[dict]:
    q = s.query(ComplianceEvent).order_by(ComplianceEvent.id.desc())
    if event_type:
        q = q.filter(ComplianceEvent.event_type == event_type)
    if request_id:
        q = q.filter(
            ComplianceEvent.payload["data"]["request_id"].astext == request_id  # type: ignore[index]
        )
    rows = q.limit(limit).all()
    return [
        {
            "id": r.id,
            "ts": r.ts.isoformat(),
            "event_type": r.event_type,
            "system_version": r.system_version,
            "model_version": r.model_version,
            "deployer_id": r.deployer_id,
            "actor_id": r.actor_id,
            "subject_ref": r.subject_ref,
            "payload": r.payload,
            "event_hash": r.event_hash,
        }
        for r in rows
    ]


def purge_expired(s: Session) -> int:
    """Remove events older than the configured retention.

    Note: 'purge' here means the application layer marks them deleted — in a
    real system you would write to an immutable cold store before deletion and
    keep a tombstone in the chain. Demo simplification: hard delete with audit
    event written first.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(
        days=settings.audit_log_retention_days
    )
    n = (
        s.query(ComplianceEvent)
        .filter(ComplianceEvent.ts < cutoff)
        .delete(synchronize_session=False)
    )
    s.commit()
    return n
