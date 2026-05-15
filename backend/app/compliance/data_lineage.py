"""Article 10 — Data governance: provenance, lineage, bias examination.

This module owns the provenance register for every dataset that fed the model.
In a real system, lineage entries are emitted by the data pipeline as it runs.
In the demo they are seeded so the API can return a complete record.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models import DataLineageRecord


SEED_LINEAGE = [
    {
        "dataset_id": "ds-cv-train-v1",
        "source": "Internal anonymised CV corpus + synthetic augmentation",
        "collection_method": (
            "Consented historical CVs from EU/EEA candidates, pseudonymised "
            "before ingest; augmented with synthetic CVs generated under a "
            "documented protocol."
        ),
        "licence_basis": "GDPR Art. 6(1)(f) + Art. 10(5) AI Act for bias correction",
        "transformations": [
            "PII redaction (names, addresses, photos, dates of birth)",
            "Locale tagging",
            "Structured extraction into typed schema",
            "Synthetic augmentation for under-represented locales",
            "Train/validation/test split, stratified by locale and role family",
        ],
        "bias_examination_summary": (
            "Selection-rate deltas measured across locale, age band (banded, not "
            "raw), and gender (self-declared where available). Deltas exceeding "
            "0.05 triggered targeted augmentation. Residual delta ranges and "
            "limitations documented in the model card."
        ),
        "custodian": "data-stewardship@compliance",
    },
    {
        "dataset_id": "ds-cv-eval-v1",
        "source": "Held-out evaluation set + recruiter-labelled ground truth",
        "collection_method": (
            "Same provenance as training set, never used in training, with "
            "recruiter-supplied shortlist/borderline/reject labels collected "
            "under blind protocol."
        ),
        "licence_basis": "GDPR Art. 6(1)(f) + Art. 10(5) AI Act",
        "transformations": [
            "PII redaction",
            "Locale tagging",
            "Structured extraction",
            "Blind labelling by three recruiters; majority label retained; "
            "disagreement flagged for adjudication.",
        ],
        "bias_examination_summary": (
            "Per-locale precision@3 reported. Subgroup analysis reported in the "
            "monthly bias monitoring report."
        ),
        "custodian": "data-stewardship@compliance",
    },
    {
        "dataset_id": "ds-job-descriptions-v1",
        "source": "Customer-supplied job descriptions (deployer side)",
        "collection_method": (
            "Provided by deployer via the screening API. Stored hashed; raw "
            "text retained on the application database, not the compliance DB."
        ),
        "licence_basis": "Deployer's lawful basis; processed under DPA.",
        "transformations": ["Structured extraction into typed schema"],
        "bias_examination_summary": (
            "Linguistic-bias check (e.g. gendered job titles, age cues) run on "
            "each new job description; warnings surfaced to deployer before use."
        ),
        "custodian": "deployer-or-controller",
    },
]


def seed_if_empty(s: Session) -> None:
    if s.query(DataLineageRecord).count():
        return
    now = datetime.now(timezone.utc)
    for entry in SEED_LINEAGE:
        s.add(DataLineageRecord(**entry, ts=now))
    s.commit()


def list_lineage(s: Session) -> list[dict]:
    rows = s.query(DataLineageRecord).order_by(DataLineageRecord.dataset_id).all()
    return [
        {
            "dataset_id": r.dataset_id,
            "source": r.source,
            "collection_method": r.collection_method,
            "licence_basis": r.licence_basis,
            "transformations": r.transformations,
            "bias_examination_summary": r.bias_examination_summary,
            "custodian": r.custodian,
            "recorded_at": r.ts.isoformat(),
        }
        for r in rows
    ]
