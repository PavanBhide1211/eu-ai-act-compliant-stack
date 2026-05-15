import React, { useEffect, useState } from "react";
import { COMPLIANT_API } from "../config.js";
import { useI18n } from "../i18n/I18nProvider.jsx";

const ACTIONS = ["accept", "override", "do_not_use"];

export default function OversightControls({ requestId }) {
  const { t } = useI18n();
  const [reviewerId, setReviewerId] = useState("reviewer1@example.eu");
  const [action, setAction] = useState("accept");
  const [overridden, setOverridden] = useState("shortlist");
  const [rationale, setRationale] = useState("");
  const [history, setHistory] = useState([]);
  const [status, setStatus] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  async function refresh() {
    const r = await fetch(
      `${COMPLIANT_API}/compliance/oversight/${requestId}`
    ).then((x) => x.json());
    setHistory(r);
  }

  useEffect(() => {
    refresh();
  }, [requestId]);

  async function submit() {
    setBusy(true);
    setError(null);
    setStatus(null);
    try {
      const r = await fetch(`${COMPLIANT_API}/compliance/oversight`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          request_id: requestId,
          reviewer_id: reviewerId,
          action,
          overridden_recommendation:
            action === "override" ? overridden : null,
          rationale,
        }),
      });
      const data = await r.json();
      if (!r.ok) {
        setError(data?.detail || "request failed");
      } else {
        setStatus(`OK — new status: ${data.new_oversight_status}`);
        setRationale("");
        await refresh();
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="oversight">
      <p>{t("compliance.oversight_blurb")}</p>

      <div className="form-row">
        <label>{t("compliance.reviewer_id")}</label>
        <input
          value={reviewerId}
          onChange={(e) => setReviewerId(e.target.value)}
        />
      </div>

      <div className="form-row">
        <label>{t("compliance.action")}</label>
        <select value={action} onChange={(e) => setAction(e.target.value)}>
          {ACTIONS.map((a) => (
            <option key={a}>{a}</option>
          ))}
        </select>
      </div>

      {action === "override" && (
        <div className="form-row">
          <label>{t("compliance.override_to")}</label>
          <select
            value={overridden}
            onChange={(e) => setOverridden(e.target.value)}
          >
            <option>shortlist</option>
            <option>borderline</option>
            <option>reject</option>
          </select>
        </div>
      )}

      <div className="form-row">
        <label>{t("compliance.rationale")}</label>
        <textarea
          value={rationale}
          onChange={(e) => setRationale(e.target.value)}
          rows={3}
        />
      </div>

      <button onClick={submit} disabled={busy || rationale.trim().length < 10}>
        {t("compliance.record_action")}
      </button>

      {status && <div className="ok">{status}</div>}
      {error && <div className="error">{error}</div>}

      <h3>{t("compliance.history_heading")}</h3>
      {history.length === 0 && <p className="muted">{t("compliance.no_actions")}</p>}
      <ul className="history">
        {history.map((h, i) => (
          <li key={i}>
            <strong>{h.action}</strong> by <code>{h.reviewer_id}</code> at{" "}
            {h.ts}
            {h.overridden_recommendation && (
              <> → overridden to <em>{h.overridden_recommendation}</em></>
            )}
            <div className="muted small">rationale: {h.rationale}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
