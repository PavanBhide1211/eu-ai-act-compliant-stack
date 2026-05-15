import React, { useState } from "react";
import { COMPLIANT_API } from "../config.js";
import { useI18n } from "../i18n/I18nProvider.jsx";
import OversightControls from "./OversightControls.jsx";
import AuditLogView from "./AuditLogView.jsx";
import ModelCardView from "./ModelCardView.jsx";
import BiasMonitorView from "./BiasMonitorView.jsx";

export default function ComplianceSidecar({ requestId }) {
  const { t } = useI18n();
  const [tab, setTab] = useState("oversight");

  const title = t("compliance.sidecar_title").replace(
    "{request_id}",
    requestId
  );

  return (
    <section className="sidecar">
      <h2>{title}</h2>
      <p className="muted">{t("compliance.sidecar_blurb")}</p>

      <nav className="tabs">
        {["oversight", "audit", "model_card", "bias"].map((tabKey) => (
          <button
            key={tabKey}
            className={tab === tabKey ? "active" : ""}
            onClick={() => setTab(tabKey)}
          >
            {t(`compliance.tab_${tabKey}`)}
          </button>
        ))}
      </nav>

      <div className="tab-body">
        {tab === "oversight" && <OversightControls requestId={requestId} />}
        {tab === "audit" && <AuditLogView requestId={requestId} />}
        {tab === "model_card" && <ModelCardView />}
        {tab === "bias" && <BiasMonitorView />}
      </div>

      <p className="muted small">
        {t("compliance.annex_iv_link")}:{" "}
        <a
          href={`${COMPLIANT_API}/compliance/technical-documentation.md`}
          target="_blank"
          rel="noreferrer"
        >
          /compliance/technical-documentation.md
        </a>
      </p>
    </section>
  );
}
