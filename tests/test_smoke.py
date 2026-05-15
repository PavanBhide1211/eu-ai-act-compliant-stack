"""Smoke tests — basic API surface coverage on the compliant backend."""


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["stack"] == "compliant" or "compliant" in body["name"].lower()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_screening_returns_envelope(client, sample_request_payload):
    r = client.post("/screening/score", json=sample_request_payload)
    assert r.status_code == 200, r.text
    body = r.json()
    for k in (
        "request_id",
        "recommendation",
        "score",
        "confidence",
        "explanation",
        "model_version",
        "oversight_status",
        "compliance_envelope",
    ):
        assert k in body, f"missing {k}"
    env = body["compliance_envelope"]
    for k in (
        "intended_purpose_checked",
        "input_pseudonymised",
        "audit_event_written",
        "bias_metrics_refreshed",
        "two_person_oversight_required",
        "candidate_ref",
        "bias_cohort",
    ):
        assert k in env, f"envelope missing {k}"


def test_decision_lookup(client, sample_request_payload):
    r = client.post("/screening/score", json=sample_request_payload)
    rid = r.json()["request_id"]
    r2 = client.get(f"/screening/decisions/{rid}")
    assert r2.status_code == 200
    assert r2.json()["request_id"] == rid


def test_compliance_surface_endpoints(client):
    """Every read-side compliance endpoint should answer 200."""
    paths = [
        "/compliance/intended-purpose",
        "/compliance/risk-register",
        "/compliance/data-lineage",
        "/compliance/audit-log",
        "/compliance/model-card",
        "/compliance/model-card.md",
        "/compliance/bias-monitor",
        "/compliance/technical-documentation.md",
        "/compliance/candidate-disclosure",
        "/i18n/locales",
    ]
    for p in paths:
        r = client.get(p)
        assert r.status_code == 200, f"{p} -> {r.status_code} ({r.text[:120]})"


def test_locales_listed(client):
    r = client.get("/i18n/locales")
    body = r.json()
    sup = set(body["supported"])
    # The five seeded locales should be present.
    assert {"en", "de", "fr", "es", "it"}.issubset(sup), sup


def test_candidate_disclosure_locale_aware(client):
    r_en = client.get("/compliance/candidate-disclosure?lang=en").text
    r_de = client.get("/compliance/candidate-disclosure?lang=de").text
    assert r_en != r_de
    # German locale should contain a clearly German token.
    assert any(w in r_de.lower() for w in ("ki", "system", "recruiter"))
