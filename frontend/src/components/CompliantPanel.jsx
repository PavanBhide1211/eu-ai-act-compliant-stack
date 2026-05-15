import React from "react";
import { useI18n } from "../i18n/I18nProvider.jsx";

export default function CompliantPanel({ result }) {
  const { t } = useI18n();
  return (
    <div className="panel panel-compliant">
      <h2>{t("panels.compliant_title")}</h2>
      <p className="panel-tag">{t("panels.compliant_tag")}</p>

      {!result && <div className="empty">{t("panels.empty")}</div>}

      {result && (
        <div className="result">
          <div className="rec">
            <span className={`badge rec-${result.recommendation}`}>
              {result.recommendation}
            </span>
            <span className="score">
              {t("panels.score")} {result.score}
            </span>
            <span className="confidence">
              {t("panels.confidence")}{" "}
              {result.confidence?.toFixed?.(2) ?? result.confidence}
            </span>
          </div>

          <h3>{t("panels.explanation_heading")}</h3>
          <p className="explanation">{result.explanation}</p>

          <h3>{t("panels.envelope_heading")}</h3>
          <ul className="envelope">
            <EnvelopeItem
              k={t("panels.envelope_intended")}
              v={result.compliance_envelope?.intended_purpose_checked}
            />
            <EnvelopeItem
              k={t("panels.envelope_pseudonymised")}
              v={result.compliance_envelope?.input_pseudonymised}
            />
            <EnvelopeItem
              k={t("panels.envelope_audit")}
              v={result.compliance_envelope?.audit_event_written}
            />
            <EnvelopeItem
              k={t("panels.envelope_bias")}
              v={result.compliance_envelope?.bias_metrics_refreshed}
            />
            <EnvelopeItem
              k={t("panels.envelope_two_person")}
              v={result.compliance_envelope?.two_person_oversight_required}
            />
          </ul>
          <p className="muted small">
            request_id: <code>{result.request_id}</code>
            <br />
            candidate_ref:{" "}
            <code>{result.compliance_envelope?.candidate_ref}</code> · cohort:{" "}
            <code>{result.compliance_envelope?.bias_cohort}</code>
          </p>
        </div>
      )}
    </div>
  );
}

function EnvelopeItem({ k, v }) {
  return (
    <li>
      <span className={`dot ${v ? "yes" : "no"}`} />
      <span className="k">{k}</span>
      <span className="v">{String(v)}</span>
    </li>
  );
}
