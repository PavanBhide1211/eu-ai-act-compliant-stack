import React from "react";
import { useI18n } from "../i18n/I18nProvider.jsx";

export default function TraditionalPanel({ result }) {
  const { t } = useI18n();
  return (
    <div className="panel panel-traditional">
      <h2>{t("panels.traditional_title")}</h2>
      <p className="panel-tag">{t("panels.traditional_tag")}</p>

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
          </div>
          <pre>{JSON.stringify(result, null, 2)}</pre>
          <div className="callout warn">
            {t("panels.traditional_callout")}
          </div>
        </div>
      )}
    </div>
  );
}
