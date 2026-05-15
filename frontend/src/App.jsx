import React, { useState } from "react";
import TraditionalPanel from "./components/TraditionalPanel.jsx";
import CompliantPanel from "./components/CompliantPanel.jsx";
import ComplianceSidecar from "./components/ComplianceSidecar.jsx";
import LanguageSwitcher from "./i18n/LanguageSwitcher.jsx";
import { useI18n } from "./i18n/I18nProvider.jsx";
import { COMPLIANT_API, TRADITIONAL_API } from "./config.js";

const SAMPLE_JOBS = {
  "Backend Engineer (DE)": {
    title: "Backend Engineer",
    required_skills: ["python", "fastapi", "postgres", "docker", "aws"],
    min_years_experience: 3,
    locale: "de",
    role_family: "engineering",
  },
  "Marketing Manager (FR)": {
    title: "Marketing Manager",
    required_skills: [
      "campaign management",
      "seo",
      "google analytics",
      "copywriting",
    ],
    min_years_experience: 5,
    locale: "fr",
    role_family: "marketing",
  },
};

const SAMPLE_CVS = {
  "Candidate A — strong match": {
    skills: ["python", "fastapi", "postgres", "docker", "aws", "kafka"],
    years_experience: 6,
    locale: "de",
    role_family: "engineering",
    self_reported_cohort: null,
  },
  "Candidate B — partial match": {
    skills: ["python", "django", "mysql"],
    years_experience: 2,
    locale: "de",
    role_family: "engineering",
    self_reported_cohort: null,
  },
  "Candidate C — weak match": {
    skills: ["javascript", "react", "css"],
    years_experience: 1,
    locale: "en",
    role_family: "engineering",
    self_reported_cohort: null,
  },
};


export default function App() {
  const { t } = useI18n();
  const [job, setJob] = useState(SAMPLE_JOBS["Backend Engineer (DE)"]);
  const [cv, setCv] = useState(SAMPLE_CVS["Candidate A — strong match"]);
  const [traditional, setTraditional] = useState(null);
  const [compliant, setCompliant] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  async function runBoth() {
    setBusy(true);
    setError(null);
    setTraditional(null);
    setCompliant(null);
    try {
      const [tRes, cRes] = await Promise.all([
        fetch(`${TRADITIONAL_API}/screening/score`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ cv, job }),
        }).then((r) => r.json()),
        fetch(`${COMPLIANT_API}/screening/score`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            cv,
            job,
            deployer_id: "demo-deployer",
            requested_by_user: "demo-user@example.eu",
          }),
        }).then((r) => r.json()),
      ]);
      setTraditional(tRes);
      setCompliant(cRes);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="layout">
      <header>
        <div className="header-row">
          <h1>{t("ui.app_title")}</h1>
          <LanguageSwitcher />
        </div>
        <p className="subtitle">{t("ui.subtitle")}</p>
      </header>

      <section className="inputs">
        <div className="picker">
          <label>{t("ui.job_label")}</label>
          <select
            value={Object.keys(SAMPLE_JOBS).find(
              (k) => SAMPLE_JOBS[k].title === job.title
            )}
            onChange={(e) => setJob(SAMPLE_JOBS[e.target.value])}
          >
            {Object.keys(SAMPLE_JOBS).map((k) => (
              <option key={k}>{k}</option>
            ))}
          </select>
        </div>
        <div className="picker">
          <label>{t("ui.candidate_label")}</label>
          <select
            value={Object.keys(SAMPLE_CVS).find(
              (k) =>
                JSON.stringify(SAMPLE_CVS[k].skills) ===
                JSON.stringify(cv.skills)
            )}
            onChange={(e) => setCv(SAMPLE_CVS[e.target.value])}
          >
            {Object.keys(SAMPLE_CVS).map((k) => (
              <option key={k}>{k}</option>
            ))}
          </select>
        </div>
        <button onClick={runBoth} disabled={busy}>
          {busy ? t("ui.running") : t("ui.run_button")}
        </button>
      </section>

      {error && <div className="error">Error: {error}</div>}

      <section className="grid">
        <TraditionalPanel result={traditional} />
        <CompliantPanel result={compliant} />
      </section>

      {compliant?.request_id && (
        <ComplianceSidecar requestId={compliant.request_id} />
      )}
    </div>
  );
}
