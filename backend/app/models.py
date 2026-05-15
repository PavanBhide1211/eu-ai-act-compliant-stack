"""SQLAlchemy models for the compliance store.

Each table maps to a specific obligation under the EU AI Act and is named
accordingly. Schema is conservative — additive changes only, no destructive
migrations on a live audit log.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON

from app.db import Base


def _utcnow():
    return datetime.now(timezone.utc)


class ComplianceEvent(Base):
    """Article 12 automatic event log. Append-only, chained-hash, tamper-evident.

    Each record references the previous record's hash via `prev_hash` and stores
    its own hash in `event_hash`. Any modification breaks the chain and is
    detectable by replaying it.
    """
    __tablename__ = "compliance_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, nullable=False, default=_utcnow, index=True)
    event_type = Column(String(64), nullable=False, index=True)
    system_id = Column(String(128), nullable=False)
    system_version = Column(String(64), nullable=False)
    model_version = Column(String(64), nullable=True)
    deployer_id = Column(String(128), nullable=True)
    actor_id = Column(String(128), nullable=True)         # human reviewer if any
    subject_ref = Column(String(128), nullable=True)      # hashed candidate ID
    payload = Column(JSON, nullable=False, default=dict)  # event-specific data
    prev_hash = Column(String(128), nullable=False)
    event_hash = Column(String(128), nullable=False, unique=True)


class Decision(Base):
    """Decision record for each CV screening request.

    Stores the recommendation, the confidence, the explanation, the model
    version, and references to the inputs in hashed form (raw inputs live in
    the application DB, not here).
    """
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, nullable=False, default=_utcnow, index=True)
    request_id = Column(String(64), nullable=False, unique=True, index=True)
    candidate_ref = Column(String(128), nullable=False)   # hashed
    job_ref = Column(String(128), nullable=False)         # hashed
    recommendation = Column(String(32), nullable=False)   # shortlist / borderline / reject
    score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False)
    model_version = Column(String(64), nullable=False)
    # Inferred or self-reported sensitive attributes used only for bias monitoring
    # under Article 10(5) safeguards. Stored pseudonymised here.
    bias_cohort = Column(String(64), nullable=True)
    oversight_status = Column(String(32), nullable=False, default="pending")
    # pending / accepted / overridden / do_not_use


class OversightAction(Base):
    """Article 14 human-oversight intervention record."""
    __tablename__ = "oversight_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, nullable=False, default=_utcnow, index=True)
    decision_request_id = Column(String(64), nullable=False, index=True)
    reviewer_id = Column(String(128), nullable=False)
    action = Column(String(32), nullable=False)   # accept / override / do_not_use
    overridden_recommendation = Column(String(32), nullable=True)
    rationale = Column(Text, nullable=False)


class DataLineageRecord(Base):
    """Article 10 data-governance lineage entry.

    One row per dataset / transformation step used during training or evaluation
    of the model that produced a decision.
    """
    __tablename__ = "data_lineage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, nullable=False, default=_utcnow, index=True)
    dataset_id = Column(String(128), nullable=False, index=True)
    source = Column(String(256), nullable=False)
    collection_method = Column(String(128), nullable=False)
    licence_basis = Column(String(128), nullable=False)
    transformations = Column(JSON, nullable=False, default=list)
    bias_examination_summary = Column(Text, nullable=True)
    custodian = Column(String(128), nullable=False)


class BiasMetric(Base):
    """Rolling subgroup metrics used for Article 15 monitoring."""
    __tablename__ = "bias_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, nullable=False, default=_utcnow, index=True)
    cohort_a = Column(String(64), nullable=False)
    cohort_b = Column(String(64), nullable=False)
    metric = Column(String(64), nullable=False)   # e.g. selection_rate_delta
    value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    alert = Column(Boolean, nullable=False, default=False)


class RiskRegisterEntry(Base):
    """Article 9 risk-management system entries."""
    __tablename__ = "risk_register"

    id = Column(Integer, primary_key=True, autoincrement=True)
    risk_id = Column(String(32), nullable=False, unique=True)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(64), nullable=False)
    severity = Column(String(16), nullable=False)
    likelihood = Column(String(16), nullable=False)
    mitigations = Column(JSON, nullable=False, default=list)
    residual_risk = Column(String(16), nullable=False)
    last_reviewed = Column(DateTime, nullable=False, default=_utcnow)
    reviewer = Column(String(128), nullable=False)
