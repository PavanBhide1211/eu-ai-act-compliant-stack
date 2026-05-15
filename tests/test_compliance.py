"""Compliance-conformance tests.

One test per Article 8-15 control. Each test verifies the control is wired and
produces the evidence the EU AI Act expects. These tests are intentionally
narrow — they confirm the architecture is in place. A real conformity
assessment will go far deeper into each obligation.
"""

import json
import time
import uuid


# =============================================================================
# Article 8 — Intended purpose
# =============================================================================
def test_article_8_intended_purpose_declared(client):
    r = client.get("/compliance/intended-purpose")
    assert r.status_code == 200
    body = r.json()
    # The declared purpose must be present and the risk tier must be set.
    assert body["intended_purpose"], "Article 8: intended purpose missing"
    assert body["risk_classification"]["tier"] in {
        "high_risk",
        "limited_risk",
        "minimal",
    }, "Article 8: risk classification must be declared"
    # A prohibited declaration must not be running.
    assert body["risk_classification"]["tier"] != "prohibited"
    # Provider identity and contact for redress.
    assert body.get("provider"), "Article 8: provider identity missing"
    assert body.get("provider_contact"), "Article 8: provider contact missing"


# =============================================================================
# Article 9 — Risk-management system
# =============================================================================
def test_article_9_risk_register_populated(client):
    r = client.get("/compliance/risk-register")
    assert r.status_code == 200
    risks = r.json()
    assert isinstance(risks, list) and len(risks) >= 3, (
        "Article 9: risk register must contain a non-trivial set of risks"
    )
    required_keys = {
        "risk_id",
        "title",
        "description",
        "category",
        "severity",
        "likelihood",
        "mitigations",
        "residual_risk",
        "last_reviewed",
        "reviewer",
    }
    for risk in risks:
        missing = required_keys - set(risk)
        assert not missing, f"Article 9: risk register entry missing {missing}"
        assert risk["mitigations"], "Article 9: every risk must have mitigations"


# =============================================================================
# Article 10 — Data governance
# =============================================================================
def test_article_10_data_lineage_populated(client):
    r = client.get("/compliance/data-lineage")
    assert r.status_code == 200
    lineage = r.json()
    assert lineage, "Article 10: data lineage register must not be empty"
    for entry in lineage:
        assert entry["source"], "Article 10: source missing"
        assert entry["collection_method"], "Article 10: collection method missing"
        assert entry["licence_basis"], "Article 10: licence/legal basis missing"
        assert entry["transformations"], "Article 10: transformations missing"
        assert entry["bias_examination_summary"], (
            "Article 10: bias examination summary missing"
        )


# =============================================================================
# Article 11 + Annex IV — Technical documentation pack
# =============================================================================
def test_article_11_annex_iv_documentation_pack(client):
    r = client.get("/compliance/technical-documentation.md")
    assert r.status_code == 200
    body = r.text
    # All eight Annex IV headings must be present.
    for heading in [
        "General description of the AI system",
        "Detailed description of elements and development process",
        "Information about monitoring, functioning and control",
        "Risk-management system",
        "Relevant changes through the lifecycle",
        "Harmonised standards applied",
        "EU declaration of conformity",
        "Post-market monitoring system",
    ]:
        assert heading in body, f"Annex IV: heading '{heading}' missing"


# =============================================================================
# Article 12 — Automatic event logging (chained, tamper-evident)
# =============================================================================
def test_article_12_audit_log_chain_intact_after_decisions(
    client, sample_request_payload
):
    # Make a couple of decisions to populate the log.
    for _ in range(2):
        r = client.post("/screening/score", json=sample_request_payload)
        assert r.status_code == 200
    r = client.post("/compliance/audit-log/verify")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True, "Article 12: chain reported broken"
    assert body["events"] >= 2, "Article 12: events should have been recorded"


def test_article_12_audit_log_records_decision_event(
    client, sample_request_payload
):
    r = client.post("/screening/score", json=sample_request_payload)
    rid = r.json()["request_id"]
    # Fetch the log filtered to this request.
    r2 = client.get(f"/compliance/audit-log?request_id={rid}")
    assert r2.status_code == 200
    events = r2.json()["events"]
    types = {e["event_type"] for e in events}
    assert "screening_decision" in types, (
        "Article 12: screening_decision event must be logged for every decision"
    )


# =============================================================================
# Article 13 — Transparency to deployers (model card)
# =============================================================================
def test_article_13_model_card_complete(client):
    r = client.get("/compliance/model-card")
    assert r.status_code == 200
    card = r.json()
    for key in (
        "system",
        "intended_purpose",
        "risk_classification",
        "prohibited_uses",
        "declared_accuracy",
        "known_limitations",
        "human_oversight_design",
        "datasets",
        "risks",
        "logging",
        "contact_for_redress",
    ):
        assert key in card, f"Article 13: model card missing '{key}'"
    assert card["declared_accuracy"], "Article 13: declared accuracy required"
    assert card["contact_for_redress"], "Article 13: redress contact required"


# =============================================================================
# Article 14 — Human oversight (intervene / override / refuse)
# =============================================================================
def test_article_14_oversight_actions_recorded(
    client, sample_request_payload
):
    r = client.post("/screening/score", json=sample_request_payload)
    rid = r.json()["request_id"]

    # accept by reviewer1
    a = client.post(
        "/compliance/oversight",
        json={
            "request_id": rid,
            "reviewer_id": "reviewer1@example.eu",
            "action": "accept",
            "rationale": "Reviewed CV and confirmed match.",
        },
    )
    assert a.status_code == 200
    body = a.json()
    assert body["new_oversight_status"] == "accepted"

    # two-person rule: same reviewer cannot act again
    again = client.post(
        "/compliance/oversight",
        json={
            "request_id": rid,
            "reviewer_id": "reviewer1@example.eu",
            "action": "accept",
            "rationale": "Reviewed CV again, still match.",
        },
    )
    assert again.status_code == 400, (
        "Article 14: two-person rule should reject same reviewer acting twice"
    )


def test_article_14_rationale_required(client, sample_request_payload):
    r = client.post("/screening/score", json=sample_request_payload)
    rid = r.json()["request_id"]
    bad = client.post(
        "/compliance/oversight",
        json={
            "request_id": rid,
            "reviewer_id": "reviewerX@example.eu",
            "action": "accept",
            "rationale": "ok",  # too short
        },
    )
    assert bad.status_code == 400, (
        "Article 14: insufficient rationale must be rejected"
    )


# =============================================================================
# Article 15 — Accuracy, robustness, cybersecurity (bias monitor + structured I/O)
# =============================================================================
def test_article_15_bias_monitor_produces_metrics(
    client, sample_request_payload
):
    # Make several decisions to generate cohort data.
    for _ in range(8):
        client.post("/screening/score", json=sample_request_payload)
    r = client.post("/compliance/bias-monitor/recompute")
    assert r.status_code == 200
    body = r.json()
    assert "rates" in body and "metrics" in body, (
        "Article 15/72: bias monitor must publish rates and metrics"
    )


def test_article_15_typed_output_constraint(client, sample_request_payload):
    """The model's output must be constrained to the typed schema, never
    free-form. We verify that score/confidence are floats and recommendation
    is from the allowed enum — both true for the stub and required of any
    real-provider implementation."""
    r = client.post("/screening/score", json=sample_request_payload)
    body = r.json()
    assert isinstance(body["score"], (int, float))
    assert isinstance(body["confidence"], (int, float))
    assert body["recommendation"] in {"shortlist", "borderline", "reject"}


# =============================================================================
# Article 50 — Candidate-facing transparency (locale-aware)
# =============================================================================
def test_article_50_candidate_disclosure_localised(client):
    en = client.get("/compliance/candidate-disclosure?lang=en").text
    de = client.get("/compliance/candidate-disclosure?lang=de").text
    fr = client.get("/compliance/candidate-disclosure?lang=fr").text
    assert en and de and fr
    assert len({en, de, fr}) == 3, "Article 50: locales should produce distinct copy"
    # Mention of AI in each locale (rough sanity).
    for txt in (en, de, fr):
        assert any(token in txt.lower() for token in ("ai", "ia", "ki")), (
            "Article 50: disclosure should reference AI"
        )
