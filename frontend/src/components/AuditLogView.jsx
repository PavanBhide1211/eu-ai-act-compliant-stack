import React, { useEffect, useState } from "react";
import { COMPLIANT_API } from "../config.js";
import { useI18n } from "../i18n/I18nProvider.jsx";

export default function AuditLogView({ requestId }) {
  const { t } = useI18n();
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(
      `${COMPLIANT_API}/compliance/audit-log?request_id=${encodeURIComponent(
        requestId
      )}`
    )
      .then((r) => r.json())
      .then(setData);
  }, [requestId]);

  if (!data) return <div className="muted">Loading...</div>;

  return (
    <div>
      <p>{t("compliance.audit_blurb")}</p>

      <div className={`chain-verify ${data.verification.ok ? "ok" : "bad"}`}>
        <strong>
          {data.verification.ok
            ? t("compliance.chain_ok")
            : t("compliance.chain_broken")}
        </strong>{" "}
        ({data.verification.events} events)
      </div>

      <table className="audit">
        <thead>
          <tr>
            <th>ts</th>
            <th>type</th>
            <th>actor</th>
            <th>subject</th>
            <th>hash</th>
          </tr>
        </thead>
        <tbody>
          {data.events.map((e) => (
            <tr key={e.id}>
              <td>{e.ts}</td>
              <td>{e.event_type}</td>
              <td>
                <code>{e.actor_id || "—"}</code>
              </td>
              <td>
                <code>{e.subject_ref || "—"}</code>
              </td>
              <td>
                <code>{e.event_hash.slice(0, 12)}…</code>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
