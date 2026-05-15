# Part 1 — The EU AI Act, in plain language

> *Audience: business stakeholders, executives, product owners, and anyone whose company sells into or operates in the European Union.*

## What is the EU AI Act?

The European Union's **Artificial Intelligence Act** — formally **Regulation (EU) 2024/1689** — is the world's first comprehensive, horizontal law governing the development, placing on the market, and use of artificial intelligence systems. It was adopted by the European Parliament and the Council in 2024, entered into force on **1 August 2024**, and is being phased in over a multi-year window that runs through 2027.

Unlike data-protection legislation such as the GDPR, which regulates what you do with personal data, the AI Act regulates **the AI system itself** — what it does, how risky it is, how it was built, how it is monitored, and what guarantees the provider gives to the people affected by its outputs. The Act applies to a far wider surface area than personal data alone: it covers safety, fundamental rights, fairness, transparency, accountability, and human oversight.

The Act is **horizontal**, meaning it applies across all sectors (HR, finance, health, education, public administration, manufacturing, retail, and so on) rather than being sector-specific. It is also **risk-based**, meaning the obligations it places on you scale with how dangerous regulators have judged the use case to be.

## Who is bound by it?

The Act's reach is deliberately broad. It applies to:

- **Providers** that place an AI system on the EU market or put it into service in the EU, regardless of where the provider itself is established.
- **Deployers** (the entities using an AI system under their authority) located inside the EU.
- **Providers and deployers established outside the EU** if the output of the AI system is used in the EU.
- **Importers and distributors** of AI systems sold into the EU.
- **Product manufacturers** that integrate AI as a safety component into products already covered by existing EU product-safety law.

In practical terms: if your AI system or its outputs touch an EU resident or an EU business, the Act applies to you, even if your company has no European office.

## The risk-tier model

The Act sorts AI systems into four tiers. The obligations you carry are determined by which tier your system falls into.

### Tier 1 — Unacceptable risk (prohibited outright)

These are use cases the EU has decided cannot lawfully be deployed at all. They are listed in **Article 5** and include, in summary form: social scoring by public authorities; cognitive-behavioural manipulation that causes harm; exploitation of vulnerabilities tied to age, disability, or socio-economic status; untargeted scraping of facial images to build recognition databases; emotion inference in the workplace or in schools (with narrow exceptions); biometric categorisation that infers sensitive attributes such as race, political opinion, or sexual orientation; and real-time remote biometric identification in publicly accessible spaces for law enforcement (with narrow, judicially supervised exceptions). These prohibitions became applicable on **2 February 2025**.

### Tier 2 — High-risk

These are AI systems where the EU accepts that the benefit can outweigh the harm, **provided** strict obligations are met. There are two routes into the high-risk tier:

- **Annex I** — AI systems that are safety components of products already covered by EU product-safety legislation (medical devices, machinery, toys, aviation, automotive, marine, lifts, and so on).
- **Annex III** — AI systems used in specific listed domains. These include biometric identification and categorisation; critical infrastructure management; education and vocational training (admissions, scoring, behavior monitoring); employment and workers management (CV screening, performance evaluation, task allocation); access to essential private and public services (credit scoring, insurance pricing, public benefit eligibility); law enforcement; migration, asylum, and border control; and administration of justice and democratic processes.

The demo in this repository implements a use case from Annex III, point 4(a): **AI-assisted CV screening**. This is a deliberate choice because the high-risk tier is where the bulk of the Act's substantive obligations live, and it is where most enterprise AI projects with a real business case actually sit.

### Tier 3 — Limited risk (transparency obligations)

These are systems whose risk is primarily about people being deceived or unaware they are interacting with AI. The Act imposes specific **transparency duties** on:

- Chatbots and conversational AI (users must be informed they are interacting with an AI, unless this is obvious).
- AI-generated or AI-manipulated audio, image, video, or text content — must be labelled as artificially generated or manipulated, with deepfakes specifically called out.
- Emotion-recognition and biometric-categorisation systems (where not prohibited) — affected persons must be informed.

### Tier 4 — Minimal risk

Everything else — spam filters, AI in video games, simple recommendation features for non-essential content. The Act does not impose specific obligations here but encourages adherence to voluntary codes of conduct.

### Plus: General-Purpose AI (GPAI) models

The Act adds a separate, parallel regime for **general-purpose AI models** — foundation models like large language models that can be adapted to many downstream tasks. GPAI providers must publish a sufficiently detailed summary of training data, comply with EU copyright law, provide technical documentation, and (if the model exceeds the systemic-risk threshold, currently defined around training compute) carry out model evaluations, adversarial testing, incident reporting, and cybersecurity protections. GPAI obligations became applicable on **2 August 2025**.

## The timeline you need to plan around

The Act phases in over a four-year window. The dates that matter:

| Date | What becomes applicable |
|---|---|
| **1 Aug 2024** | Regulation enters into force. |
| **2 Feb 2025** | Article 5 prohibitions apply. AI literacy obligation for staff begins. |
| **2 Aug 2025** | GPAI obligations apply. Governance bodies (AI Office, AI Board, national authorities) operational. Penalty regime active for the items above. |
| **2 Aug 2026** | Most remaining provisions apply. **Annex III high-risk obligations become enforceable.** This is the date most enterprises are planning towards. |
| **2 Aug 2027** | Annex I high-risk obligations (AI as safety components of regulated products) apply. |

If you sell a product or run an internal AI system in the EU that touches an Annex III domain, **2 August 2026** is the date that should be on your roadmap. As of the publication of this demo (May 2026), that deadline is roughly three months away.

## Penalties

Non-compliance is expensive by design. The Act tiers penalties so that the worst violations attract the largest fines:

- **Prohibited practices (Article 5)** — up to **€35 million or 7% of total worldwide annual turnover**, whichever is higher.
- **Most other obligations** (high-risk system requirements, transparency, GPAI obligations, etc.) — up to **€15 million or 3% of worldwide annual turnover**.
- **Supplying incorrect, incomplete, or misleading information** to authorities — up to **€7.5 million or 1% of worldwide turnover**.
- Lower caps apply to SMEs and start-ups, but the percentage exposure is still material.

Penalties for breaches of GPAI obligations are subject to their own cap structure (up to €15 million or 3% of worldwide turnover), administered by the EU AI Office.

## What this means for a business operating in Europe

Strip the legal language away and the practical implications fall into five buckets.

The first is **scope discovery**. Most companies do not have an authoritative list of every AI system they operate. The Act forces you to build that inventory and to classify each item by risk tier. This sounds clerical; in practice it is the single most important and most under-budgeted compliance task. You cannot meet obligations on systems you do not know you have.

The second is **architectural rework on high-risk systems**. High-risk AI systems must satisfy the requirements in Articles 8 to 15: a documented risk-management system, robust data governance with attention to representativeness and bias, technical documentation, automatic event logging, transparency that lets the deployer understand and use the system correctly, meaningful human oversight, and demonstrable accuracy, robustness, and cybersecurity. These are not a checklist of policies — they are properties the system has to have. Retrofitting them onto an existing system is more expensive than designing them in from the start, which is why this demo is structured around showing what "built-in from day one" looks like.

The third is **governance and operating-model change**. Providers must operate a Quality Management System covering AI lifecycle, document conformity assessments, register the system in the EU database, and run post-market monitoring with serious-incident reporting. Deployers have parallel duties: they must use the system as intended, monitor it, maintain logs, ensure human oversight by competent staff, and conduct fundamental-rights impact assessments where required. Roles, accountabilities, and authority lines need to be redrawn.

The fourth is **third-party and supply-chain due diligence**. If you deploy an AI system from a vendor, the obligations under the Act do not disappear — they are split between you and the provider. Your procurement, vendor-risk, and contract templates need to reflect the Act's allocation of duties, which means engaging legal, security, and procurement teams before the renewal cycle, not at it.

The fifth is **workforce capability**. The Act introduces a baseline **AI literacy** obligation: organisations placing AI systems on the market or deploying them must ensure their staff have a sufficient level of AI literacy, calibrated to the context of use. This is not optional and it is not a one-off training — it is a continuing duty.

## Why this matters even if you are not in a "high-risk" domain

There are three reasons to take this seriously even if you believe none of your systems is high-risk.

First, classification is not always obvious. A general HR analytics product can drift into Annex III if it starts being used to evaluate candidates or workers. A recommendation engine in a public service can drift into Annex III if it starts influencing access to essential services. The Act's scope expands with your use case.

Second, the **transparency obligations under Article 50** apply across many systems — including chatbots and any system that generates synthetic content. These obligations are lighter than the high-risk regime, but they still require product changes (disclosure UX, content labelling and watermarking) and they apply broadly.

Third, **GPAI provisions** apply to anyone hosting or substantially fine-tuning foundation models that meet the GPAI definition. Many companies that consider themselves "just users" of a large language model may, depending on how they fine-tune or deploy it, fall into GPAI-provider territory.

## How the demo helps

The rest of this repository takes everything above and turns it into a working system you can run, point at, and discuss with customers. The next two documents — `02-service-provider-implications.md` and `03-operational-aspects.md` — translate the Act into duties for service providers and into daily operational practices. The code in `backend/` and `frontend/` (Day 2) then shows what those duties look like as endpoints, audit records, model cards, oversight controls, and bias monitoring. The `traditional-stack/` companion shows the same use case built the way most teams build it today, so the gap is visible side by side.
