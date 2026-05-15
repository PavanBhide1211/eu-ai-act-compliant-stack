# Part 3 — Critical operational aspects of the EU AI Act

> *Audience: engineering leads, product managers, MLOps, risk and compliance officers, and the people who will actually run a compliant AI system day to day.*

This document does not restate the regulation. It takes the obligations from Parts 1 and 2 and converts them into the operating practices, controls, artefacts, and cadences a real business has to put in place. It is organised around the AI lifecycle, because that is how the obligations attach in practice, and it ends with a concrete operating-model section that names roles, RACI, and the cadence on which each control must run.

## The mental model: compliance is a property of the lifecycle, not the model

The most useful frame for operationalising the AI Act is to stop thinking about "the model" as the regulated artefact. The regulated artefact is the **AI system as a lifecycle** — design, data, training, validation, integration, deployment, monitoring, change management, incident response, decommissioning. Every one of those stages produces evidence the Act expects you to be able to show, and every one of those stages must have controls that constrain what the next stage can do.

If you take a snapshot of a compliant AI system in production, what you should see is not just a model and an API. You should see, attached to the model: a documented intended purpose; a risk register that has been reviewed; a dataset card describing provenance, lineage, and bias-testing results; a technical documentation pack; an event log being written in real time; transparency artefacts available to the deployer; an active human-in-the-loop oversight design; a monitoring stack with thresholds and alerts; a change-management workflow; and a post-market monitoring dashboard. None of those is optional, and none of them can be bolted on at the end without leaving gaps.

## Stage 1 — Intended purpose and risk classification

Every obligation in the Act keys off the **intended purpose** the provider declares for the system. This is not a marketing description. It is a binding statement that defines: what the system is meant to do, on whom, in what context, by whom (the operator profile), with what data, and to produce what kind of output and decision. The intended purpose is the document against which the conformity assessment is run and against which any future change is judged "substantial" or not.

Operationally, this means:

The intended purpose must be **written before the system is built**, not after. In practice it lives as a short, dated, version-controlled document that the product owner authors and the legal/compliance function counter-signs. The Day 2 codebase carries it as a `system_intended_purpose.yaml` file checked into the repo and read at boot.

A **risk classification decision** must be recorded for each system. Use a simple decision tree: prohibited (Article 5) → high-risk (Annex I or III) → limited risk (Article 50 transparency) → minimal. The decision must record the reasoning, not just the outcome. Where Annex III is even arguably in scope, classify as high-risk and proceed accordingly; the cost of over-classifying is small relative to the cost of mis-classifying.

A **change-control rule** must be agreed up front: who is authorised to alter the intended purpose, what process they must follow, and what re-classification (and re-assessment) is triggered by which kinds of change.

## Stage 2 — Risk-management system

Article 9 requires a **risk-management system** that runs across the lifecycle. This is the spine of compliance for high-risk systems. The operational components are:

- **Hazard identification** for known and reasonably foreseeable risks to health, safety, and fundamental rights — including risks to children, vulnerable groups, and groups disproportionately represented in the training data.
- **Risk estimation and evaluation** under both intended use and reasonably foreseeable misuse.
- **Adoption of risk-management measures** — design changes, mitigation in the training process, instructions for use, transparency, oversight design — chosen with reference to the state of the art and balanced against the residual risk.
- **Testing** procedures that verify the chosen measures actually achieve their purpose, performed throughout the development process and at appropriate points thereafter.

A risk register exists in most enterprises already. The AI-specific differences are: it must be linked to the intended purpose, it must include foreseeable misuse (not only failure modes), and it must be reviewed on a defined cadence and after every substantial change. The Day 2 backend exposes the risk register as a versioned, queryable object so deployers can inspect it.

## Stage 3 — Data governance

Article 10 is one of the operationally heaviest parts of the Act. The practices that satisfy it are:

A **data provenance register** for every dataset used in training, validation, and testing. Each entry records: source, collection method, collection date, licence/legal basis, sensitive-attribute coverage, transformations applied, and the person or team who collected it. The register is queryable from the system itself — meaning your data pipeline writes provenance metadata as it goes, rather than reconstructing it later.

A **dataset card** per dataset describing what the dataset is, what it is meant to represent, known limitations, and the results of bias examination. Dataset cards are not optional in this regime; they are evidence.

A **representativeness assessment** of training data relative to the population the system will be used on, including geography, demographics, behaviour patterns, and any sensitive attributes relevant to the use case.

A **bias examination** that detects skew likely to cause harm or unlawful discrimination, performed before training, after training, and on an ongoing basis. Where bias is detected, **corrective measures** are documented and re-tested — bias examination without a corrective loop is not compliance.

**Special-category data handling** under Article 10(5): if special-category data is processed for bias correction, the controls (purpose limitation, pseudonymisation, access controls, prompt deletion, no third-party transmission) are evidenced in the data pipeline itself, not in a PDF.

## Stage 4 — Technical documentation

Article 11 and **Annex IV** specify what the technical documentation pack must contain for a high-risk AI system. The pack is not a single document — it is a structured set of artefacts that together describe the system end to end. The Annex IV table of contents is, in operational terms:

1. General description of the AI system: intended purpose, providers, version, hardware, deployment forms, instructions for use.
2. Detailed description of the elements and process of development: design choices, optimization, design specifications, training methodology, datasets, validation and testing procedures, metrics, cybersecurity measures.
3. Detailed information about monitoring, functioning, and control: capabilities and limitations, accuracy levels (including for specific groups), expected outputs, foreseeable unintended outcomes, human oversight measures, technical measures to facilitate interpretation of outputs.
4. Description of the risk-management system.
5. Description of relevant changes through the lifecycle.
6. List of harmonised standards applied (and, where they were not, the technical solutions adopted).
7. Copy of the EU declaration of conformity.
8. Detailed description of the post-market monitoring system.

Operationally, this pack must be **kept current** — not assembled the week before an inspection. The pragmatic pattern is to generate it from the same sources of truth used to run the system: dataset cards, model cards, risk register, change log, monitoring dashboards. The Day 2 codebase includes a `compliance/docgen.py` module that emits an Annex IV–shaped PDF from those sources on demand.

## Stage 5 — Automatic logging

Article 12 requires automatic logging of events relevant to risk identification and post-market monitoring. The operational requirements that follow:

A **dedicated, append-only event log** distinct from application logs. The compliant pattern is a separate table or store (in the Day 2 demo, a `compliance_events` SQLite table) with a stable schema, no overwrite, and tamper-evidence (a chained hash per record at minimum).

A **defined schema** covering at least: timestamp, system version and model version, input fingerprint (hashed, not raw, except where Article 10(5) safeguards apply), output, confidence score, deployer ID, deployer-side user ID (if known), oversight action taken, and any flag set by monitoring.

A **retention period** that is documented, defensible, and at least as long as the provider's instructions require. Six months is the floor that appears in the Act for some categories; longer is normal in practice. Retention must be balanced against GDPR data-minimisation; the combination is typically: keep the log, redact or hash any personal data inside it, retain the log itself for the duration the AI Act and contracts require.

A **query interface** so deployers and authorities can extract evidence on request, without engineering involvement.

## Stage 6 — Transparency to deployers and to affected persons

Two transparency duties operate in parallel.

The first is **Article 13 transparency to deployers**: instructions for use that allow deployers to understand the system's capabilities, limitations, intended purpose, level of accuracy (including for specific persons or groups), known foreseeable misuses, the characteristics of the training/validation/test data relevant to its intended purpose, and the human-oversight measures the provider has designed in. Operationally this is a **model card and an instructions-for-use document** that ship with the system and are accessible from inside it.

The second is **Article 50 transparency to affected persons**: notifying users that they are interacting with an AI system (chatbots), labelling AI-generated or AI-manipulated content, informing affected persons when emotion-recognition or biometric-categorisation systems are used on them, and labelling deepfakes. Operationally this is **UX work** — disclosure copy, visible labels, watermarks on synthetic content — plus a content-provenance pipeline for any media the system generates.

## Stage 7 — Human oversight

Article 14 requires that human oversight be **designed into the system**. It is not enough to say "a human reviews the output." The Act expects:

The system to be designed so that natural persons can **understand its capabilities and limitations**, **detect and address anomalies, malfunctions, and unexpected performance**, **interpret the output correctly**, **decide not to use the system in a particular case or to disregard, override, or reverse its output**, and **intervene or interrupt operation through a stop button or similar procedure**.

For systems that can identify or categorise persons (and by extension for any decision-support system whose outputs materially affect a person), oversight must be exercised by **at least two natural persons with the necessary competence, training, and authority**, unless Union or national law explicitly provides otherwise.

The operational pattern is to build the oversight UX as a first-class feature of the system: an "intervention" endpoint that records the human reviewer's identity, decision, and reasoning; a "do-not-use" toggle that visibly disables the AI's recommendation for a given case; and an "override and capture rationale" flow that pipes the reviewer's reasoning back into the audit log. The Day 2 frontend renders all three.

## Stage 8 — Accuracy, robustness, cybersecurity

Article 15 requires the system to achieve appropriate levels of accuracy, robustness, and cybersecurity, and to perform consistently in those respects through its lifecycle. Operationally:

**Accuracy metrics**, including subgroup metrics, are defined before development starts, measured at validation, declared in the instructions for use, and continuously monitored in production.

**Robustness** is engineered against: input drift, label drift, distribution shift, adversarial inputs, and reasonably foreseeable edge cases. Robustness is tested before release and monitored after.

**Cybersecurity** treats the model and its training pipeline as in-scope assets. The current attack surface (data poisoning, model poisoning, evasion attacks, model extraction, prompt injection for generative systems, supply-chain attacks on dependencies and model weights) must be threat-modelled and mitigated.

**Feedback loops** that would cause the system's own outputs to bias its future training data are identified and addressed. This is one of the under-recognised failure modes; if your model recommends candidates and your downstream hiring data is shaped by those recommendations, you create a self-reinforcing bias loop unless you intervene.

## Stage 9 — Quality Management System

Article 17 requires a documented **Quality Management System (QMS)**. The familiar reference points are ISO 9001 and ISO/IEC 42001 (AI management systems). The QMS covers, at minimum:

- A strategy for regulatory compliance.
- Techniques and procedures for the design, development, quality control, and quality assurance of the AI system.
- Examination, test, and validation procedures, including data-management procedures.
- Technical specifications and standards applied.
- Procedures for data management throughout the lifecycle.
- The risk-management system referred to in Article 9.
- Post-market monitoring (Article 72).
- Procedures for serious-incident reporting (Article 73) and for communication with competent authorities.
- Record-keeping.
- Resource management, including supply-of-security measures.
- Accountability — the framework setting out responsibilities of management and other staff for all aspects of compliance.

For most organisations, the QMS is an extension of an existing ISO-flavoured management system, not a parallel one. The work is to (a) make sure each clause has an actual owner inside the organisation, (b) make sure the AI-specific procedures are documented and live, and (c) hook the QMS to a cadence of internal audits.

## Stage 10 — Conformity assessment and CE marking

Article 43 requires a **conformity assessment** before a high-risk AI system is placed on the market. For most Annex III systems the route is **internal control** — the provider verifies, against the Annex IV documentation, that the system meets the Articles 8–15 requirements, then draws up the **EU declaration of conformity** under Article 47 and affixes the **CE marking** under Article 48. For specific systems (notably some biometric identification systems), **third-party conformity assessment** by a notified body is required.

The system must then be **registered in the EU database** under Article 71 before it is placed on the market or put into service.

Internal control is not a self-certification rubber stamp. The provider must produce, and be ready to show, the technical documentation, the QMS, the test results, and the declaration of conformity. The CE mark on the product is what gives a deployer or an authority the right to assume those underlying artefacts exist.

## Stage 11 — Post-market monitoring

Article 72 requires the provider to operate a **post-market monitoring system** that systematically collects, documents, and analyses performance data over the system's lifetime. Operationally:

A **monitoring plan** is documented up front, specifying the metrics watched, their thresholds, who reviews them and on what cadence, and what triggers what action.

The **monitored signal set** is at minimum: declared accuracy versus realised accuracy (overall and per subgroup), drift signals on inputs and outputs, oversight intervention rate, complaint and contestation rate from affected persons, incident counts, and any specific metrics declared in the intended purpose.

The **dashboard** is reviewed at a defined cadence — daily by the operational owner, weekly or monthly by the compliance owner — and reviews are logged.

The **feedback path into the QMS** is explicit: monitoring findings flow into the risk-management system as inputs to the next review cycle, and substantive findings trigger change management.

## Stage 12 — Serious-incident reporting

Article 73 requires that **serious incidents** — defined as incidents leading or contributing to death, serious damage to health, serious and irreversible disruption of critical infrastructure, infringement of fundamental rights, or serious damage to property or the environment — be reported to the market surveillance authority of the affected Member State.

The deadlines are tight and they matter:

| Incident category | Deadline from awareness |
|---|---|
| Widespread infringements or breakdown of critical infrastructure | Immediately |
| Death of a person | No later than 2 days |
| Serious and irreversible disruption / serious harm to health or property / fundamental-rights infringement | No later than 10 days |
| Otherwise | No later than 15 days |

These are calendar days, and the clock starts on **awareness** — not on confirmation, root cause, or any internal decision. The operational implication is that the **internal incident-response runbook must be calibrated to the regulatory clock**, with a "have we seen this kind of thing before?" gate that triggers immediate compliance notification while engineering still has the incident open.

## The operating model — who does what

For a high-risk AI system in production, the minimum role set is:

- **Product owner** — owns the intended purpose, the business case, the deployer-facing documentation, and the change requests.
- **Engineering / MLOps lead** — owns the technical implementation of the Article 9–15 controls and the integrity of the data and event-log pipelines.
- **AI risk and compliance officer** — owns the QMS, the risk register, the conformity assessment file, the registration in the EU database, and the relationship with the market surveillance authority.
- **Data protection officer / privacy lead** — owns the GDPR overlay, the DPIA, and the lawful-basis analysis under Article 10(5) where applicable.
- **Fundamental Rights Impact Assessment owner** (deployer-side, for many Annex III deployments) — typically the legal, HR, or operations function that consumes the system.
- **Human oversight reviewers** — the named staff who exercise oversight in production, with documented competence and authority.
- **Incident commander** — owns the response to serious incidents and the regulator-facing communication, integrated with the existing incident-management function.

A practical RACI assigns the product owner and the engineering lead as accountable for the technical and product duties, the AI compliance officer as accountable for the regulatory artefacts, and the DPO as accountable for the privacy overlay, with each consulted on the others' work. The oversight reviewers are accountable for individual decisions but not for the system; the incident commander is accountable for response but not for prevention.

## The cadence

Reduce the regulation to a calendar and the operational picture clarifies further.

**Continuously**: event logging, monitoring, alerting on threshold breach.

**Per release / per substantial change**: re-run risk-management review, refresh dataset cards and model card, re-run bias examination, update technical documentation, re-confirm conformity, log the change in the change register.

**Weekly**: dashboard review by the engineering and compliance owners, with sign-off recorded.

**Monthly**: post-market monitoring report compiled and reviewed; oversight intervention sample audit; complaint-and-contestation review.

**Quarterly**: risk register review with the product owner, compliance officer, and DPO; FRIA refresh on material change; QMS internal audit on a rotation.

**Annually**: full conformity-assessment refresh; QMS external audit (where applicable); training refresh for oversight staff; AI-literacy programme review for all relevant staff.

**Immediately on an incident**: trigger the incident runbook; assess the regulator-notification clock against Article 73; preserve evidence including the event log; coordinate with the deployer if you are the provider, or with the provider if you are the deployer.

## How the demo embodies this

The codebase delivered on Days 2 and 3 turns the practices above into running components.

`backend/app/compliance/intended_purpose.py` loads and serves the intended-purpose document and exposes the change-control gate.

`backend/app/compliance/risk_register.py` is a versioned object store for the Article 9 risk register, queryable by deployers.

`backend/app/compliance/data_lineage.py` writes provenance and lineage records as data is ingested and transformed.

`backend/app/compliance/bias_monitor.py` computes subgroup metrics on every batch of decisions and emits alerts on drift.

`backend/app/compliance/audit_log.py` writes the Article 12 event log with chained hashes to an append-only store.

`backend/app/compliance/oversight.py` exposes intervention, do-not-use, and override-with-rationale endpoints.

`backend/app/compliance/model_card.py` and `backend/app/compliance/docgen.py` generate the model card and the Annex IV technical documentation pack on demand.

`frontend/src/components/ComplianceSidecar.tsx` renders the audit log, the intervention controls, and the model card in the UI alongside the AI's recommendation — so a user can see, at the moment of decision, the evidence they would need in order to override.

The `traditional-stack/` baseline implements the same CV-screening API surface with none of the above. The contrast is the demo.

Part 4 walks through the architecture and the code. Part 5 makes the whole thing available in five EU languages, with a one-command path to add a sixth.
