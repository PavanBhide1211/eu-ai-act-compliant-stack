import React, { useEffect, useState } from "react";
import { COMPLIANT_API } from "../config.js";
import { useI18n } from "../i18n/I18nProvider.jsx";

export default function BiasMonitorView() {
  const { t } = useI18n();
  const [data, setData] = useState(null);
  const [busy, setBusy] = useState(false);

  async function refresh() {
    const r = await fetch(`${COMPLIANT_API}/compliance/bias-monitor`).then(
      (x) => x.json()
    );
    setData(r);
  }

  useEffect(() => {
    refresh();
  }, []);

  async function recompute() {
    setBusy(true);
    await fetch(`${COMPLIANT_API}/compliance/bias-monitor/recompute`, {
      method: "POST",
    });
    await refresh();
    setBusy(false);
  }

  if (!data) return <div className="muted">Loading...</div>;

  return (
    <div>
      <p>{t("compliance.bias_blurb")}</p>

      <button onClick={recompute} disabled={busy}>
        {busy ? "..." : t("compliance.recompute")}
      </button>

      <h4>Current selection rates</h4>
      <table>
        <thead>
          <tr>
            <th>Cohort</th>
            <th>Selection rate</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(data.rates || {}).map(([k, v]) => (
            <tr key={k}>
              <td>{k}</td>
              <td>{Number(v).toFixed(3)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h4>Recent metrics</h4>
      <table>
        <thead>
          <tr>
            <th>ts</th>
            <th>cohort_a</th>
            <th>cohort_b</th>
            <th>delta</th>
            <th>alert</th>
          </tr>
        </thead>
        <tbody>
          {(data.recent_metrics || []).map((m, i) => (
            <tr key={i} className={m.alert ? "row-alert" : ""}>
              <td>{m.ts}</td>
              <td>{m.cohort_a}</td>
              <td>{m.cohort_b}</td>
              <td>{Number(m.value).toFixed(4)}</td>
              <td>{m.alert ? "ALERT" : "ok"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
