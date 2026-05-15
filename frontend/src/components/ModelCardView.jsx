import React, { useEffect, useState } from "react";
import { COMPLIANT_API } from "../config.js";
import { useI18n } from "../i18n/I18nProvider.jsx";

export default function ModelCardView() {
  const { t } = useI18n();
  const [card, setCard] = useState(null);

  useEffect(() => {
    fetch(`${COMPLIANT_API}/compliance/model-card`)
      .then((r) => r.json())
      .then(setCard);
  }, []);

  if (!card) return <div className="muted">Loading...</div>;

  return (
    <div>
      <p>{t("compliance.model_card_blurb")}</p>

      <h3>
        {card.system.id} <span className="muted">{card.system.version}</span>
      </h3>
      <p>
        <strong>Risk:</strong> {card.risk_classification.tier} —{" "}
        {card.risk_classification.basis}
      </p>
      <p>{card.intended_purpose}</p>

      <h4>Declared accuracy</h4>
      <ul>
        {Object.entries(card.declared_accuracy || {}).map(([k, v]) => (
          <li key={k}>
            <strong>{k}:</strong> {String(v)}
          </li>
        ))}
      </ul>

      <h4>Prohibited uses</h4>
      <ul>
        {card.prohibited_uses.map((p, i) => (
          <li key={i}>{p}</li>
        ))}
      </ul>

      <h4>Known limitations</h4>
      <ul>
        {card.known_limitations.map((p, i) => (
          <li key={i}>{p}</li>
        ))}
      </ul>

      <h4>Datasets</h4>
      <ul>
        {card.datasets.map((d) => (
          <li key={d.id}>
            <strong>{d.id}</strong>: {d.source} ({d.licence_basis})
          </li>
        ))}
      </ul>

      <h4>Top risks (residual)</h4>
      <ul>
        {card.risks.slice(0, 5).map((r) => (
          <li key={r.id}>
            <strong>
              {r.id} — {r.title}
            </strong>{" "}
            ({r.residual_risk})
          </li>
        ))}
      </ul>

      <p className="small">
        Contact for redress:{" "}
        <code>{card.contact_for_redress}</code>
      </p>
    </div>
  );
}
