# Part 2 — What the EU AI Act means for service providers and data handlers

> *Audience: hosting providers, SaaS vendors, model providers, integrators, consultancies, system integrators, and any party that touches AI on someone else's behalf.*

## Why service providers cannot treat this as somebody else's problem

The EU AI Act assigns duties to roles, not to companies. A single company can — and very often does — occupy more than one role at once, and each role carries its own obligations. If you build, host, fine-tune, integrate, resell, or operate AI on behalf of a customer, you are not standing outside the Act's perimeter. You are inside it, and the question is only which set of duties attaches to you and for which system.

This document maps the four operative roles the Act defines, explains what each one owes, and then works through the consequences for the categories of service provider most exposed in practice: model hosts, SaaS platforms, system integrators, and data processors. It closes with the interplay between the AI Act and the GDPR, because for almost every service provider those two regimes will land at the same time on the same workload.

## The four operative roles

The Act builds its allocation of duties on four roles, defined in Article 3 and operationalized throughout the regulation.

A **Provider** is a natural or legal person that **develops** an AI system or has it developed and **places it on the market or puts it into service under its own name or trademark**, whether for payment or free of charge. Providers carry the lion's share of the substantive obligations: they design the system, they conduct the conformity assessment, they affix the CE marking, they register the system in the EU database, and they own the post-market monitoring duty.

A **Deployer** (referred to in earlier drafts as "user") is a natural or legal person using an AI system **under its authority**, in the course of a professional activity. Deployers must follow the provider's instructions, exercise human oversight by competent staff, keep automatically generated logs when those logs are under their control, and — for many Annex III systems — carry out a Fundamental Rights Impact Assessment before deployment.

An **Importer** brings an AI system from outside the EU and places it on the EU market under the name of a non-EU provider. Importers must check that the provider has done its job (technical documentation, conformity assessment, CE marking) before putting the system on the market, and they share responsibility for any defects discovered later.

A **Distributor** is anyone in the supply chain other than the provider or importer who makes the system available on the EU market. Distributors have lighter but still real duties: verifying CE marking and documentation are present, not making the system available if they have reason to believe it does not conform, and cooperating with authorities.

A critical mechanic to internalise: under **Article 25**, a deployer or distributor can be **re-classified as a provider** if they put their own name or trademark on a system, substantially modify it, or change its intended purpose in a way that makes it high-risk. This re-classification triggers the full provider obligation stack. For service providers, this is the single most common path from "we just operate someone else's model" to "we are legally a provider and we did not know."

## What service providers actually owe — by role they typically occupy

### When you are a model host or model API provider

If you host or expose a model that meets the **general-purpose AI model** definition (broad capability across many downstream tasks, generally a large language or multimodal model), the GPAI obligations apply to you under Articles 53–55. You owe:

- **Technical documentation** covering model architecture, training process, data, computational resources, energy use, and evaluation results, kept current and made available to authorities on request.
- **Information and documentation for downstream providers** that integrate your model — enough that they can satisfy their own AI Act obligations.
- A **policy to comply with EU copyright law**, including respect for opt-outs expressed by rights holders under the Copyright Directive.
- A **sufficiently detailed summary of training data**, published using the template issued by the AI Office.

If your model is judged to pose **systemic risk** — the current threshold is anchored on training compute exceeding 10²⁵ FLOPs, though the Commission can update it — additional obligations under Article 55 apply: model evaluations against systemic risks, adversarial testing (red-teaming), tracking and reporting of serious incidents, and adequate cybersecurity protections for the model weights and training infrastructure.

### When you are a SaaS platform delivering an AI feature

If your customers consume an AI-powered feature you have built, you are almost certainly a **Provider** with respect to that feature, even if the underlying model is supplied by someone else. The provider obligations attach to **your system as integrated**, not only to its parts.

In concrete terms this means:

- You need a **risk-management system (Article 9)** that runs across the AI system's lifecycle and is documented.
- You need **data and data-governance practices (Article 10)** for training, validation, and test data, including representativeness, examination for bias, and appropriate measures to detect and correct bias.
- You need **technical documentation (Article 11 and Annex IV)** before the system is placed on the market and kept up to date thereafter.
- You need **automatic logging (Article 12)** of events relevant to risk identification and post-market monitoring, retained for an appropriate period.
- You need **transparency to deployers (Article 13)** through instructions for use that allow them to understand the system's capabilities, limitations, intended purpose, expected accuracy, and oversight measures.
- You need **human oversight (Article 14)** designed in such a way that natural persons can effectively oversee the system, intervene, and override outputs.
- You need **accuracy, robustness, and cybersecurity (Article 15)** built into the system itself, not as ops add-ons.
- You need a **Quality Management System (Article 17)** covering documentation, change management, post-market monitoring, and corrective actions.
- You need a **conformity assessment (Article 43)** before placing the system on the market — internal control for most Annex III cases, third-party assessment in specific cases (notably some biometric systems).
- You need a **CE marking** affixed to your product (or made available electronically).
- You need to **register the system in the EU database (Article 71)** before placing it on the market.
- You need **post-market monitoring (Article 72)** and **serious-incident reporting (Article 73)** to the relevant national authority within tight deadlines (immediately for widespread infringements or breakdowns; within 15 days otherwise; within 2 days for serious incidents that involve death).

### When you are a system integrator or implementation partner

If you customise, fine-tune, or substantially modify an AI system for a customer, **Article 25** is the article you must read carefully. Three things will tip you from "implementation partner" to "Provider in your own right":

1. Putting your name or trademark on the integrated system.
2. Making a **substantial modification** — a change that affects compliance with the requirements or that changes the intended purpose in a way that the original conformity assessment no longer covers.
3. **Re-purposing** the system into a high-risk use case it was not originally intended for.

Any of those triggers means the customer's provider duties become **your** provider duties for the modified system. In practice this hits consultancies and implementation partners who fine-tune a foundation model on customer data and then deploy it for a high-risk use case. From the moment that fine-tuned system goes into production, you are very likely the provider of a new high-risk AI system.

### When you are a data processor (in GDPR terms) for an AI system

Data processors do not have a named role under the AI Act — the Act regulates AI systems, not personal data flows. But the moment the data you process is fed into an AI system covered by the Act, your work intersects two regimes. You will need to:

- Satisfy your GDPR Article 28 processor obligations under your DPA (instructions, confidentiality, sub-processors, security, deletion/return, assistance).
- **Cooperate with your controller** when they conduct the Fundamental Rights Impact Assessment under Article 27 of the AI Act for high-risk deployments.
- **Cooperate with your controller** on data governance obligations: provenance, lineage, representativeness, bias mitigation, and (where applicable) lawful processing of special categories of data for bias-correction purposes under Article 10(5).
- **Cooperate on logging**: many of the events the AI Act requires to be logged will be created or stored on your infrastructure. The contractual arrangement must make these logs accessible to the controller for the required retention period.

## Data obligations, in more detail

For Annex III high-risk systems trained on data, Article 10 requires that training, validation, and test datasets satisfy specific quality criteria. The criteria you must be able to evidence include:

- **Relevant design choices** documented for data collection processes and provenance.
- **Data preparation** operations such as annotation, labelling, cleaning, updating, enrichment, and aggregation documented and traceable.
- **Assumptions** about what the data is supposed to measure and represent, made explicit.
- **Assessment of availability, quantity, and suitability** of the datasets needed.
- **Examination in view of possible biases** that may affect health, safety, or fundamental rights or that may lead to discrimination prohibited by Union law.
- **Appropriate measures to detect, prevent, and mitigate** identified biases.
- **Identification of data gaps or shortcomings** and how they are addressed.

Datasets must be **sufficiently representative and, to the best extent possible, free of errors and complete in view of the intended purpose**. They must also have appropriate statistical properties for the persons or groups on which the system is intended to be used, considering the geographical, behavioural, contextual, or functional setting.

Article 10(5) — an important provision often missed — permits the **processing of special categories of personal data** for the purposes of bias detection and correction in high-risk AI systems, subject to safeguards including pseudonymisation, access controls, no transmission to third parties, and prompt deletion once the bias-correction purpose has been met. This is one of the rare places where the AI Act explicitly authorises a processing operation that GDPR would normally restrict.

## Logging and traceability — what processors and hosts actually have to capture

Article 12 obligates providers to design high-risk systems with **automatic event logging**. The minimum content of the log set depends on the use case, but for systems involving biometric identification (and by analogy, for any system whose decisions can materially affect a person) the logs must record at least:

- The period of each use, identified by start and end timestamps.
- The reference database against which input data has been checked.
- The input data for which the search resulted in a match.
- The identification of the natural persons involved in the verification of the results.

For service providers, this means three concrete things. First, the **log schema must be designed deliberately** — it is not whatever happens to fall into your application logs. Second, **logs must be retained** in line with the provider's instructions or, in their absence, for an appropriate period (typically at least six months, often longer). Third, **logs must be readable and producible on request** by the deployer and, ultimately, by authorities.

The reference implementation in this repository (Day 2) shows a concrete schema and retention policy for these logs.

## Post-market monitoring and incident reporting

Once a high-risk AI system is on the market, the Act expects active monitoring rather than fire-and-forget deployment.

- **Article 72 — Post-market monitoring system**: providers must establish and document a post-market monitoring system that systematically collects, documents, and analyses data on the performance of the system throughout its lifetime, allowing the provider to evaluate continued compliance.
- **Article 73 — Reporting of serious incidents**: providers must report any **serious incident** to the market surveillance authorities of the affected Member States. Deadlines are tight: immediately for widespread infringements; **no later than 15 days** after awareness in general; **no later than two days** where the incident involves death of a person; and within 10 days for incidents involving serious harm.

Service providers (especially SaaS providers) are usually the first to see indicators of a serious incident — error rates, drift signals, anomalous outputs, complaints. The operational reality is that **your monitoring stack is the upstream detector for the provider's regulatory reporting deadline**. Misalignment between your incident-response runbook and the provider's reporting clock is one of the most common — and most expensive — gaps in real deployments.

## Interplay with the GDPR

The AI Act does not replace the GDPR. It sits on top of it. For service providers, the practical consequences are:

- **Two parallel impact assessments** for many high-risk AI use cases: a **DPIA** under GDPR Article 35 for the personal-data processing, and a **Fundamental Rights Impact Assessment (FRIA)** under AI Act Article 27 for the deployment of the high-risk system. They overlap but are not the same; the FRIA is broader in subject matter (fundamental rights generally, not just data protection) but narrower in trigger (only specific high-risk deployments).
- **Different lead authorities**. GDPR work is overseen by Data Protection Authorities. AI Act work is overseen by national **market surveillance authorities** designated under the AI Act, supported at EU level by the **AI Office** within the European Commission and the **AI Board** of Member State representatives. Some Member States are co-locating the two; others are not. Plan for two regulator relationships.
- **Overlapping but not identical record-keeping**. GDPR Article 30 records of processing and AI Act Article 11 / Annex IV technical documentation cover related ground but ask different questions. Build both, ideally from the same source of truth.
- **Article 10(5) AI Act vs. Article 9 GDPR**. AI Act Article 10(5) creates a narrow lawful basis for processing special-category data to detect and correct bias in high-risk AI systems. GDPR Article 9 still applies and its conditions must be satisfied independently. Co-counsel between data-protection and AI-compliance functions is required here; this is not a place to copy a sample clause.

## The contractual surface that has to change

If you are a service provider, the changes the AI Act forces into your contracts are concrete and non-trivial. At minimum:

- **Allocation of provider/deployer/importer/distributor roles**, explicitly named and tied to each AI system delivered.
- **Documentation flow-down**: who supplies the technical documentation, instructions for use, and conformity records, and on what cadence.
- **Logging and log-access** terms: schema, retention, access, format, and cost of extraction.
- **Incident-reporting cooperation**: notification timelines that allow the provider to meet the Article 73 deadlines.
- **Monitoring data flow-back**: agreement on which signals are routed to the provider for post-market monitoring.
- **Substantial-modification trigger language**: what counts as a substantial modification and what happens to roles and liability when it occurs.
- **Audit and inspection rights**: scope and notice, including for unannounced inspections by authorities.
- **Sub-processor and sub-provider chains**: visibility, approval, and cascading obligations.

For service providers operating in regulated industries (financial services, healthcare, public sector) the contractual surface widens further to include sector-specific oversight and resilience expectations (DORA, MDR, e-procurement frameworks, and so on).

## The bottom line

For a service provider, "supporting AI for our customer" is a regulated activity under the EU AI Act from the moment the AI system enters scope. The role you play — provider, deployer, importer, distributor, or some combination — determines the duties you owe, and your role can change based on what you put your name on or how substantially you modify the system. The duties are technical (logging, transparency, oversight controls, bias monitoring, cybersecurity) and procedural (risk management, quality management, documentation, conformity assessment, post-market monitoring, incident reporting). And they sit on top of, not instead of, your existing GDPR and sector-specific obligations.

The next document — `03-operational-aspects.md` — translates these duties into the day-to-day operating model: who does what, on what cadence, with which tools, and against which metrics.
