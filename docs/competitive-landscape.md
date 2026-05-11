# Competitive Landscape
## Network Operations, Observability, and Agentic Incident Response

**Audience:** VP of Product, Cisco / Splunk
**Author:** Bharat Namatherdhala
**Date:** May 2026
**Companion document:** `docs/prd.md`

---

## Executive Summary

Vigil sits at the intersection of three product categories — network-specialist operations tools, observability platforms, and agentic AI assistants. No single competitor today combines all three, which is the white space Vigil targets.

**The headline:**

| Capability | Network Specialists (Juniper, Aruba, Arista) | Observability Platforms (Datadog, Dynatrace, New Relic) | AIOps Platforms (BigPanda, Moogsoft, ServiceNow) | **Vigil** |
|---|:---:|:---:|:---:|:---:|
| Cisco Catalyst topology + Splunk telemetry in one investigation | ❌ | ❌ | ❌ | ✅ |
| Multi-step agentic investigation with auditable state machine | ❌ | Partial (single-turn assistants) | ❌ | ✅ |
| Foundation-model time-series forecasting (multi-trigger) | ❌ | Statistical only | ❌ | ✅ |
| Pinecone Retrieval-Augmented Generation incident memory | ❌ | ❌ | ❌ | ✅ |
| Per-investigation token-cost measurement | ❌ | ❌ | ❌ | ✅ |
| Pre-triage suppression at zero tokens | ❌ | ❌ | Partial (event correlation) | ✅ |

The competitive question is not whether Vigil's components are individually novel. Foundation models exist, vector stores exist, finite state machines exist. **The novelty is the integration and the specific application to Cisco + Splunk network operations** — and the architecture's readiness to absorb Cisco's roadmap (Deep Network Model, AI Canvas, Skills Registry) as those components ship.

---

## The Market Map

The competitive space organizes along two axes: **scope** (network-specialist vs. general observability) and **autonomy** (reactive correlation vs. agentic investigation).

```
                          AGENTIC / AUTONOMOUS INVESTIGATION
                                       ▲
                                       │
                  Cisco AgenticOps      │      AWS DevOps Agent + Splunk
                  (preview, 2025–26)    │      (generally available, April 2025)
                  Juniper Marvis        │      Datadog Bits AI
                  (generative assistant)│      (single-turn assistant)
                                        │      Dynatrace Davis AI
                  ╔═══════════════════╗ │      (causal AI, automatic root cause)
                  ║      VIGIL         ║│
                  ║  network + agentic ║│
                  ║  + Splunk + Cisco  ║│
                  ╚═══════════════════╝ │
                                        │
   ─── NETWORK ────────────────────────┼───────────────────── GENERAL ─────►
   ── SPECIALIST ──                    │                     OBSERVABILITY
                                        │
                  HPE Aruba Central     │      Splunk IT Service Intelligence
                  AIOps                 │      Datadog Watchdog
                  Arista CloudVision    │      New Relic AI
                  CV-AI                 │      Elastic Observability
                  Extreme ExtremeCloud  │      Sumo Logic
                  Nokia NetGuard        │      LogicMonitor LM Envision
                                        │      BigPanda, Moogsoft,
                                        │      ServiceNow ITOM, PagerDuty
                                        │      AIOps, BMC Helix
                                        ▼
                          REACTIVE CORRELATION / ANALYTICS
```

**Where Vigil sits:** Upper-left quadrant (network-specialist + agentic), bridging into the upper-right (general observability + agentic) via Splunk Model Context Protocol integration. **No competitor occupies the upper-left today.** Cisco AgenticOps is closest but not shipped.

---

## Tier 1 — Direct Competitors (Network Operations + Agentic AI)

These are products targeting the same buyer (network operations) with an AI/autonomy story. Vigil's positioning is sharpest against this tier.



### Juniper Networks — Marvis (Mist AI)

| Field | Status |
|---|---|
| **What they ship today** | Marvis Virtual Network Assistant — generative AI interface for Juniper Mist (campus wireless, wired, SD-WAN). Conversational query of network state, anomaly detection, automated root cause for wireless issues. |
| **Shipping timeline** | Generally available. Strong market presence in enterprise wireless and campus networking. |
| **AI/agentic approach** | Single-turn generative assistant. Strong on conversational interface, weaker on multi-step autonomous investigation. |
| **Strengths** | Mature wireless / campus network analytics, integrated with Juniper hardware, strong customer mindshare on "AI for networking" |
| **Gaps relative to Vigil** | (1) Juniper-hardware-only — does not investigate Cisco infrastructure. (2) Single-turn agent — no multi-step Finite State Machine with auditable transitions. (3) No Splunk integration. (4) No forecasting layer with confidence intervals. (5) No structured audit trail for compliance. |
| **Vigil's posture** | Different hardware ecosystem; Vigil targets Cisco-shop enterprises. Where the two overlap (mixed-vendor environments), Vigil's Splunk integration and multi-step Finite State Machine are differentiators. |

### HPE Aruba Networking Central — AIOps

| Field | Status |
|---|---|
| **What they ship today** | Aruba Central with AIOps — anomaly detection, predictive Wi-Fi capacity planning, automated peer benchmarking across Aruba Central deployments |
| **Shipping timeline** | Generally available |
| **AI/agentic approach** | Statistical anomaly detection, threshold-based predictive analytics. Not foundation-model driven. Not agentic. |
| **Strengths** | Large customer base in enterprise wireless / campus / branch, peer benchmarking across deployments is a unique data advantage |
| **Gaps relative to Vigil** | (1) Aruba hardware focus — not a Cisco competitor in Cisco shops. (2) Reactive only — no agentic investigation. (3) No multi-step reasoning. (4) No Splunk integration. (5) No foundation-model forecasting. |
| **Vigil's posture** | Different hardware ecosystem. Vigil is the Cisco-shop equivalent of what Aruba ships, plus agentic capability. |

### Arista Networks — CloudVision + CV-AI

| Field | Status |
|---|---|
| **What they ship today** | CloudVision (network management platform) with CV-AI (autonomous networks). Focus on data-center and cloud networking, telemetry-driven automation. |
| **Shipping timeline** | Generally available; CV-AI capabilities are evolving |
| **AI/agentic approach** | Telemetry-driven anomaly detection, predictive capacity planning. Strong on streaming network telemetry; less developed on conversational / agentic interface. |
| **Strengths** | Best-in-class streaming telemetry, strong data-center focus, EOS programmability |
| **Gaps relative to Vigil** | (1) Arista-only — does not investigate Cisco infrastructure. (2) Data-center focus, not enterprise campus. (3) No Splunk Processing Language Retrieval-Augmented Generation. (4) No multi-step Finite State Machine. (5) No conversational / agentic incident commander. |
| **Vigil's posture** | Different hardware ecosystem and different segment focus (Vigil = Cisco enterprise; Arista = data-center). |

### Extreme Networks — ExtremeCloud IQ CoPilot

| Field | Status |
|---|---|
| **What they ship today** | ExtremeCloud IQ CoPilot — generative AI assistant for Extreme Networks customers, anomaly detection, conversational network query |
| **AI/agentic approach** | Conversational assistant; less mature than Marvis but in the same product category |
| **Gaps relative to Vigil** | Hardware-locked to Extreme. Smaller customer base. Single-turn assistant. No Splunk or Cisco integration. |
| **Vigil's posture** | Different hardware ecosystem. |

### Nokia — NetGuard / Network Services Platform

| Field | Status |
|---|---|
| **What they ship today** | NetGuard (security analytics for telco), Network Services Platform (operations for IP/optical/microwave). AI capabilities exist for fault correlation and capacity planning. |
| **AI/agentic approach** | Telco-focused; carrier-grade, not enterprise |
| **Gaps relative to Vigil** | Telco-only customer base. Different operations model from enterprise Cisco shops. |
| **Vigil's posture** | Different segment (telco vs. enterprise). Not directly competitive. |

---

## Tier 2 — Adjacent Competitors (General Observability + Agentic AI)

These products target a broader buyer (observability / Site Reliability Engineering) and are adding agentic capabilities. They overlap with Vigil through Splunk integration or through the autonomous investigation pattern.

### AWS DevOps Agent + Splunk

| Field | Status |
|---|---|
| **What they ship today** | Autonomous AI agent integrated with Splunk Observability Cloud (April 2025). Investigates software / application incidents, surfaces root cause hypotheses, suggests remediation. |
| **Shipping timeline** | Generally available |
| **AI/agentic approach** | Single-turn investigation per alert, returns hypothesis and suggested action. The closest live product to Vigil's pattern. |
| **Strengths** | Live, shipping, Amazon Web Services-backed, integrated with Splunk |
| **Gaps relative to Vigil** | (1) Application / software stack focus — not network infrastructure. (2) No Cisco Catalyst topology awareness. (3) Single-turn, not multi-state Finite State Machine. (4) No pre-triage suppression. (5) No Border Gateway Protocol / interface-layer coverage. (6) No blast radius classification. |
| **Vigil's posture** | Different incident scope. AWS DevOps Agent proves the agentic-Splunk-investigation market exists; Vigil owns the network-specialist sub-segment that AWS is not addressing. |

### Datadog — Bits AI + Watchdog

| Field | Status |
|---|---|
| **What they ship today** | Bits AI (generative assistant for Datadog data, single-turn conversational query). Watchdog (statistical anomaly detection across application performance monitoring, logs, real-user monitoring). |
| **Shipping timeline** | Generally available |
| **AI/agentic approach** | Bits AI is single-turn conversational; Watchdog is backward-looking anomaly detection |
| **Strengths** | Enormous customer base, integrated across full observability stack, polished user interface |
| **Gaps relative to Vigil** | (1) Application performance monitoring focus, not network infrastructure. (2) No Cisco Catalyst integration. (3) No multi-step Finite State Machine. (4) Watchdog is anomaly detection, not forecasting — backward-looking only. (5) No Splunk Processing Language Retrieval-Augmented Generation. (6) Different buyer (Site Reliability Engineering / developer, not network operator). |
| **Vigil's posture** | Different buyer and different infrastructure layer. Customers in Cisco shops typically run Splunk and Datadog in parallel — Vigil targets the Splunk side. |

### Dynatrace — Davis AI

| Field | Status |
|---|---|
| **What they ship today** | Davis AI — causal artificial intelligence, automatic root cause analysis, generative AI assistant. Strong on application performance monitoring with automatic topology-aware causality. |
| **Shipping timeline** | Generally available, mature product line |
| **AI/agentic approach** | Causal AI — uses dependency mapping to automatically determine root cause without manual rule configuration. One of the more sophisticated AI offerings in observability. |
| **Strengths** | Best-in-class automatic root cause analysis for application performance monitoring, strong customer mindshare on "deterministic AI" positioning |
| **Gaps relative to Vigil** | (1) Application focus, not network infrastructure. (2) Causal AI works on observed dependencies; does not forecast forward. (3) No Cisco Catalyst integration. (4) No agentic multi-step investigation — Davis returns an answer, not a sequenced investigation trace. (5) Different buyer. |
| **Vigil's posture** | Most credible competitor on "we have AI that explains itself," but at a different layer. Vigil's positioning vs. Dynatrace: same governance posture (transparent, accountable AI), different infrastructure layer. |

### New Relic AI

| Field | Status |
|---|---|
| **What they ship today** | New Relic AI (formerly Grok AI) — generative assistant for New Relic data, query generation, anomaly explanation |
| **AI/agentic approach** | Single-turn conversational assistant |
| **Gaps relative to Vigil** | Application performance monitoring focus, not network. Single-turn agent. No Cisco integration. No multi-step Finite State Machine. |
| **Vigil's posture** | Different layer and different buyer. |

### Splunk Native (Splunk AI Assistant / SAIA + IT Service Intelligence)

| Field | Status |
|---|---|
| **What they ship today** | SAIA (`saia_*` Model Context Protocol tools) — Splunk Processing Language generation, optimization, explanation. IT Service Intelligence Predictive Analytics — statistical forecasting on Splunk metrics. |
| **Shipping timeline** | Generally available |
| **AI/agentic approach** | SAIA is single-turn Splunk Processing Language generation. IT Service Intelligence Predictive Analytics is per-metric statistical forecasting. Neither is agentic. |
| **Strengths** | Native to the Splunk environment, no integration burden, owned by the same Cisco family post-acquisition |
| **Gaps relative to Vigil** | SAIA does not execute queries, sequence tool calls, escalate, remediate, or produce an audit trail. IT Service Intelligence Predictive Analytics uses statistical models, not foundation models, and does not integrate with agentic investigation. |
| **Vigil's posture** | Vigil **consumes** SAIA via `saia_generate_spl` and picks up exactly where SAIA stops. Vigil's forecasting layer is the foundation-model upgrade over IT Service Intelligence Predictive Analytics' statistical approach. |

---

## Tier 3 — AIOps Platforms (Event Correlation, Not Investigation)

These products predate the foundation-model era. They correlate alerts, suppress noise, and route incidents — but do not investigate. They are losing share to the agentic-investigation category Vigil sits in.

| Vendor | Product | What It Does | Why It's Not Direct Competition |
|---|---|---|---|
| **BigPanda** | AIOps event correlation platform | Alert clustering, noise reduction, incident routing | Reactive correlation only — no investigation, no agentic capability, no forecasting |
| **Moogsoft** (Dell) | AIOps platform | Event correlation, anomaly detection | Reactive only. Acquired by Dell; product investment uncertain |
| **ServiceNow ITOM Predictive AIOps** | Operations management with AIOps add-on | Event correlation, change risk prediction, automated workflows | Workflow-engine focus, not investigation. AIOps capabilities are statistical, not agentic |
| **PagerDuty AIOps (Event Intelligence)** | On-call platform with AIOps | Alert grouping, change correlation, response automation | Incident response orchestration, not investigation. No multi-step agentic reasoning |
| **BMC Helix AIOps** | Enterprise operations management | Event correlation, predictive analytics, IT automation | Legacy enterprise focus, slower AI roadmap |
| **LogicMonitor LM Envision** | Observability + AIOps | Anomaly detection, root cause hints, dependency mapping | Mid-market focus; AI capabilities are correlation-based, not agentic |
| **IBM Watson AIOps + Instana** | AI-powered IT operations | Causal AI, automatic root cause, observability | Causal AI similar to Dynatrace; not network-specialist; mainframe / legacy enterprise bias |
| **Microsoft Sentinel** | Cloud-native Security Information and Event Management with Security Orchestration, Automation and Response | Security incident correlation, automated playbooks | Security focus, not network operations |

**The pattern:** AIOps platforms compete on **breadth of integrations and correlation accuracy**. They do not compete on **investigation depth or autonomous action**. As foundation-model agents like Vigil mature, this entire tier risks being relegated to "alert ingestion plumbing" while the agentic layer (Vigil, Cisco AgenticOps, AWS DevOps Agent) handles the decision logic.

---

## Tier 4 — Forecasting / Predictive Analytics Specialists

These products forecast metrics forward but do not investigate. They are the closest competitors to Vigil's **Phase 4 Proactive Forecasting Layer** specifically.

| Vendor | Product | Forecasting Method | Foundation Models | Multi-Trigger Logic | Agentic Investigation |
|---|---|---|---|---|---|
| **Splunk IT Service Intelligence Predictive Analytics** | Statistical models, per-metric tuning | ❌ No — statistical only | ❌ Threshold breach only | ❌ |
| **Dynatrace Davis (predictive)** | Causal AI + time-series | ❌ Statistical | ❌ Threshold only | Partial — root cause but not multi-step investigation |
| **Datadog Forecasting (Watchdog)** | Statistical time-series | ❌ | ❌ Threshold only | ❌ |
| **AWS Lookout for Metrics** | Machine learning anomaly detection on metrics | Custom Amazon Web Services models, not foundation models | ❌ Anomaly score only | ❌ |
| **New Relic Lookout** | Statistical anomaly detection | ❌ | ❌ | ❌ |
| **Anodot** | Time-series anomaly detection for business and operations metrics | ❌ Statistical / proprietary machine learning | ❌ Anomaly score only | ❌ |
| **Vigil — Forecasting Layer** | **Cisco Time Series Model + Chronos in parallel** | **✅ Two foundation models** | **✅ Threshold + Trajectory + Uncertainty** | **✅ Integrated with Finite State Machine investigation** |

**The pattern:** No forecasting specialist combines foundation models with multi-trigger logic and agentic investigation. The market has forecasting (statistical) and investigation (agentic) as separate categories. **Vigil is the only product unifying them.**

---

## Tier 5 — Adjacent Categories Worth Tracking

These are not direct competitors today but could become so as their roadmaps evolve.

| Category | Players | Why They Matter |
|---|---|---|
| **Autonomous Site Reliability Engineering agents** | Resolve.ai, Cleric, Patterns.app, OpsLevel | New category of AI agents specifically for incident investigation. Currently focused on software / application incidents, but the architecture is similar to Vigil's. Could expand into network operations. |
| **Generative network configuration** | Nile Networks, Selector AI | AI-first network-as-a-service. Different go-to-market (greenfield deployments) but shares the "autonomous network operations" pitch. |
| **Time-series foundation model providers** | Amazon Chronos, Google TimesFM, Cisco Time Series Model, Salesforce Moirai, TimeGPT (Nixtla) | Suppliers, not competitors. Vigil currently uses two; the market is maturing rapidly. |
| **Network Operations Center automation** | NetBrain, IP Fabric, Forward Networks | Network discovery, topology analysis, intent-based verification. Strong on network knowledge graphs; weak on agentic reasoning. Could partner or compete. |
| **Open-source agent frameworks** | LangGraph, CrewAI, AutoGen | Frameworks, not products. Customers could build something Vigil-like on these — but the integration and Splunk-specific knowledge is the moat. |

---

## Where Vigil Stands — The Defensible Position

Three structural advantages explain why Vigil's white space exists and why it is defensible.

### 1. Cisco + Splunk in One Investigation Loop

Splunk's Model Context Protocol server (14 tools, generally available) and Cisco's Catalyst Center (separate Model Context Protocol planned) are owned by the same company post-acquisition, but **no shipped product bridges them into a single agent's investigation**. Vigil does. Every Tier 1 competitor is locked to its own hardware (Juniper to Juniper, Aruba to Aruba). Every Tier 2 competitor is locked to its own observability data plane (Datadog to Datadog, Dynatrace to Dynatrace). Vigil is the only product that joins both stacks in one loop.

### 2. Foundation-Model Forecasting + Agentic Investigation in One System

The forecasting specialists (Tier 4) do not investigate. The agentic-investigation specialists (Tier 1 and 2) do not forecast. **Vigil is the only product where a foundation-model trigger fires the Finite State Machine investigation and the forecast snapshot becomes part of the audit trail.** This is the architecture Splunk's own 2026 predictions describe — and the architecture no competitor has shipped.

### 3. Built to Absorb Cisco's Roadmap, Not Race It

When Cisco AI Canvas ships, Vigil's Finite State Machine maps to a Canvas workflow. When the Deep Network Model ships, the Large Language Model call swaps out. The Pinecone Retrieval-Augmented Generation layers, evaluator, pre-triage classifier, forecasting layer, and audit trail all remain. **Vigil is positioned as the application that runs on Cisco's horizontal platform — not as a horizontal platform competing with Cisco.** That alignment makes the partnership story credible.

---

## The One-Sentence Competitive Statement

> Every other product in this landscape is either network-specialist (Juniper Marvis, Aruba, Arista, Extreme) **without** Splunk and agentic depth — or general observability (Datadog, Dynatrace, New Relic) **without** Cisco network specialization — or AIOps platforms (BigPanda, Moogsoft) **without** investigation depth. Vigil is the only product that combines all three: Cisco network specialization, Splunk integration, and agentic multi-step investigation with foundation-model forecasting and an auditable audit trail.

---

## Sources and Notes

- Cisco AgenticOps: Cisco Live 2025 keynote (Jeetu Patel), Cisco public roadmap materials
- AWS DevOps Agent + Splunk: Splunk Observability Cloud product announcements (April 2025)
- Splunk Security Predictions 2026, Splunk CTO Blog: Hao Yang's published predictions on Mean Time to Resolve, governance, and domain-specific small language models
- Vendor capability descriptions: synthesized from public product pages and analyst coverage; specific feature claims should be verified before quoting in customer or partner conversations
- This document is a planning artifact, not a marketing comparison. Specific competitor weaknesses cited above should be treated as starting hypotheses for sales / product positioning conversations, not as final claims
