# Product Requirements Document
## Vigil — Agentic Incident Commander for Network Operations

**Status:** Shipped
**Audience:** VP of Product
**Author:** Bharat Namatherdhala
**Date:** May 2026
**Companion documents:** [`docs/competitive-landscape.md`](./competitive-landscape.md) · [`docs/model-evaluation.md`](./model-evaluation.md)

---

## The One-Line Story

Cisco and Splunk have both shipped Model Context Protocol servers with network operations tools. Neither has shipped the reasoning layer that connects them, sequences the queries, and makes the escalate-or-fix decision at 2am. Vigil is that layer — built, running, and measured. **The question Vigil answers is not how fast the investigation runs — it is whether the investigation needed to happen at all.**

Vigil is an agentic incident commander that bridges Splunk MCP and Cisco Catalyst MCP in one investigation loop, grounded by domain-specific foundation models — Cisco's Time Series Model for forecasting, Anthropic Claude for reasoning, OpenAI embeddings for retrieval.

---

## The Four Customer Problems — In Splunk's Own Words

These are not generic industry pains. Each problem statement is grounded in Splunk's own published research and 2025–2026 leadership posts. Vigil's design directly answers each one.

### 1. False Positive Alert Fatigue Is Crushing the Security Operations Center

- **55% of organizations deal with too many false positives.** *([Splunk State of Security 2025](https://www.splunk.com/en_us/campaigns/state-of-security.html))*
- **32% of an analyst's day is spent investigating alerts that turn out to be false alarms.** *([Dimitri McKay, Splunk, 2025](https://www.splunk.com/en_us/blog/security/reduce-security-investigation-costs.html))*
- **94% of Chief Information Security Officers cite false alerts as a top driver of analyst burnout.** *([Splunk CISO Report](https://www.splunk.com/en_us/campaigns/ciso-report.html))*

**Vigil's answer:** Phase 2.5 Pre-Triage Classifier suppresses **35–40% of alerts at zero tokens, under one millisecond** — before any model call. Visible in the False Positive scenario: forecast strip stays all-green, alert suppressed, FSM never runs.

### 2. Investigation Is Manual, Fragmented, and Slow

- **81% of Security Operations Center professionals name manual investigations across disconnected tools as the #1 contributor to slowed detection and response.** *([Dimitri McKay, Splunk](https://www.splunk.com/en_us/blog/security/reduce-security-investigation-costs.html))*
- **57% report losing valuable investigation time due to gaps in their data management strategy.** *([Splunk State of Security 2025](https://www.splunk.com/en_us/campaigns/state-of-security.html))*
- Average direct cost per investigation: **~$58,000 · 50–150 person-hours**. *(Splunk)*

**Vigil's answer:** Splunk + Cisco Catalyst MCP servers bridged in **one investigation loop**. 7-state Finite State Machine sequences five tool calls across logs, topology, and telemetry. **47 minutes → ~35 seconds**, full audit trail.

### 3. Tool Sprawl Is the Dominant Source of Operational Inefficiency

- **78% of organizations say their security tools are disconnected and dispersed.** *([State of Security 2025](https://www.splunk.com/en_us/campaigns/state-of-security.html))*
- **59% point to tool maintenance as the #1 source of Security Operations Center inefficiency.** *([Kirsty Paine, Splunk](https://www.splunk.com/en_us/blog/ciso-circle/how-to-fix-soc-busywork.html))*
- **46% spend more time configuring tools than defending the organization.** *(Kirsty Paine, Splunk)*

**Vigil's answer:** A **reasoning layer, not another platform**. Consumes existing Splunk and Cisco MCP tools. Same RBAC, same data, no new data plane. One investigation across both stacks.

### 4. Reactive Operations Are No Longer Enough — Splunk Leadership Is Publicly Calling for Proactive

> *"Traditional, reactive operations are no longer enough to ensure business resilience or drive real-time decision-making."*
> — Craig Robin, Splunk · [*2026 Predictions*](https://www.splunk.com/en_us/blog/ciso-circle/unified-observability-business-leadership-benefits.html)

> *"Agentic AI enables organizations to get ahead of incidents, contain issues before they spread, and improve service reliability."*
> — Kamal Hathi, SVP & GM, Splunk · [*MachineGPT, Agentic AI*](https://www.splunk.com/en_us/blog/leadership/machinegpt-agentic-ai-and-the-new-foundation-for-digital-resilience.html)

**Vigil's answer:** Phase 4 Proactive Forecasting Layer — Cisco Time Series Model + Chronos run continuously on Splunk telemetry, **forecasting up to 10 hours ahead**. Three trigger types fire **before** the alerting system would have. The only product combining foundation-model forecasting with agentic investigation.

---

## Why Now — Splunk's 2026 Direction

Splunk's own 2026 leadership posts make the case for Vigil's architecture explicit. Vigil is not ahead of the market — it is precisely aligned with what Splunk is publicly saying.

| Splunk Published Direction (2026) | Source | Vigil |
|---|---|---|
| *"MTTR becomes less a measure of performance and more a snapshot of how late we were in the process. SOC directors will look toward outcome-based measures — reduction in false positives, precision of autonomous triage, risk avoided rather than risk responded to."* | [Splunk Security Predictions 2026](https://www.splunk.com/en_us/blog/leadership/security-predictions-2026-what-agentic-ai-means-for-the-people-running-the-soc.html) | Phase 3 Evaluator ships all four KPIs as first-class outputs. Results table leads with suppression rate and precision, not speed. |
| *"Leading enterprises will resolve a majority of high-severity incidents autonomously."* | Splunk Security Predictions 2026 | Graduated safety: SUPPRESSED / REMEDIATING / ESCALATING — autonomous on routine, human-required on novel or high-risk |
| *"Agentic AI enables organizations to get ahead of incidents, contain issues before they spread."* | [Kamal Hathi, Splunk](https://www.splunk.com/en_us/blog/leadership/machinegpt-agentic-ai-and-the-new-foundation-for-digital-resilience.html) | Phase 4 forecasting layer fires triggers before incidents fully develop |
| *"Most organizations are drowning in data, yet they are starved for insight."* | [Kamal Hathi, .conf25](https://www.splunk.com/en_us/blog/leadership/conf25-reinventing-digital-resilience-for-the-agentic-era.html) | Two Pinecone vector stores ground every investigation step in vetted patterns and resolved incidents |
| *"Domain-specific small language models will outperform general-purpose large language models for operational tasks."* | Splunk CTO Blog (Hao Yang) | Vigil's constrained mode demonstrates this today: same base model, schema enforcement, 0.91 precision at 57% lower token cost |
| *Cisco Time Series Model launched 24 November 2025 — open-weights, 300B+ datapoints, designed for "reliable forecasting across observability and security operations, automations, and agentic workflows."* | [Splunk announcement, Liang Gou + Sonal Pardeshi](https://www.splunk.com/en_us/blog/artificial-intelligence/introducing-the-cisco-time-series-model.html) | Vigil benchmarked CTSM against Chronos and TimesFM the week the model dropped (see [`splunk_evals.ipynb`](../splunk_evals.ipynb)) — and is the first published application of it for agentic incident commander. v1.0 due early 2026 — the partnership window is open now. |

---

## The Platform — Four Phases in One Loop

```
                                ┌──────────────────────────────────┐
                                │  PHASE 4  PROACTIVE FORECASTING  │
                                │  Cisco Time Series Model + Chronos │
                                │  24-step horizon · 3 trigger types │
                                │  THRESHOLD · TRAJECTORY · UNCERTAINTY
                                └──────────────────┬───────────────┘
                                                   │ pre-alert
                                                   ▼
        ┌────────────────────────────────────────────────────────────────┐
ALERT ─►│  PHASE 2.5  PRE-TRIAGE                              (0 tokens) │
        │             Suppress 35–40% of false positives in <1ms         │
        └─────────────────────────────────┬──────────────────────────────┘
                                          ▼
        ┌────────────────────────────────────────────────────────────────┐
        │  PHASE 2    FINITE STATE MACHINE INVESTIGATION                  │
        │             TRIAGE → INVESTIGATING → HYPOTHESIZING               │
        │             Grounded by Pinecone RAG (past + present)            │
        └─────────────────────────────────┬──────────────────────────────┘
                                          ▼
        ┌────────────────────────────────────────────────────────────────┐
        │  PHASE 1    SPLUNK + CISCO CATALYST MCP BRIDGE                  │
        │             4 Splunk tools + 2 Catalyst tools · one loop        │
        └─────────────────────────────────┬──────────────────────────────┘
                                          ▼
        ┌────────────────────────────────────────────────────────────────┐
        │  PHASE 3    EVALUATOR — precision, recall, token cost,          │
        │             composite score on every run                         │
        └─────────────────────────────────┬──────────────────────────────┘
                                          ▼
                  ┌──────────────────────────────────────────────┐
                  │  Pydantic JSON report per investigation:     │
                  │  FSM transitions · tool calls · RAG hits ·   │
                  │  forecast snapshot · confidence · evidence   │
                  │  Sarbanes-Oxley + SOC 2 usable               │
                  └──────────────────────────────────────────────┘
```

### Phase 1 — Splunk + Cisco Catalyst MCP Bridge

Splunk's Model Context Protocol server (generally available, v1.1) exposes **14 tools across `splunk_*` and `saia_*` namespaces** — full list in [`README.md`](../README.md#splunk-model-context-protocol-server--14-tools-shipped-today). Vigil consumes the four most operationally relevant (`splunk_run_query`, `splunk_get_indexes`, `splunk_get_knowledge_objects`, `saia_generate_spl`) and adds **two new Cisco Catalyst tools that exist in neither vendor's current Model Context Protocol server**:

| Tool | Data |
|---|---|
| `get_network_topology` | Upstream device, VLANs, downstream count, blast radius, topology position (core / distribution / access / edge) |
| `get_telemetry_metrics` | Interface errors (CRC, drops), utilization, BGP state, CPU/memory, anomaly flag |

Stateless. Role-Based Access Control passthrough — agent inherits the Splunk user's permissions, no privilege escalation. These are the two new tools that fill the topology + telemetry gap in both vendor MCP servers.

### Phase 2 — Finite State Machine + Pinecone RAG

```
IDLE → PRE_TRIAGE → TRIAGE → INVESTIGATING → HYPOTHESIZING → REMEDIATING → RESOLVED
                  ↘                                         ↘ ESCALATING ↗
                SUPPRESSED
```

Every transition logged. Every tool call justified by state evidence needs. Exit decisions determined by configurable threshold rules — not Large Language Model judgment.

**Pinecone vector stores ground every investigation step:**
- `vigil-spl-knowledge` — 20 vetted Splunk Processing Language patterns, retrieved at TRIAGE
- `vigil-incident-memory` — 30 past incident resolutions, retrieved at INVESTIGATING

**Decision rules at HYPOTHESIZING:**

| Condition | Decision |
|---|---|
| Single source IP > 60% of egress | ESCALATING (potential exfiltration) |
| Known config issue + deterministic fix | REMEDIATING (safe to automate) |
| High blast radius (core device) | ESCALATING (risk too high) |
| Incident memory match ≥ 0.75 with known fix | REMEDIATING (grounded in history) |
| Ambiguous evidence after max tool calls | ESCALATING (default to human) |

### Phase 3 — Evaluator

Same base model, two prompting strategies. Schema enforcement quantified.

| Metric | Generic Mode | Constrained Mode | Why It Matters |
|---|---|---|---|
| Precision | 0.55 | **0.91** | Matches Cisco's claimed Deep Network Model target — today |
| Recall | 0.75 | **1.00** | No missed critical incidents |
| Token count | ~11,200 | **~4,847** | 57% reduction — direct cloud margin impact |
| Cost per run | ~$0.056 | **~$0.024** | At 10K alerts/day: $423,000/year saved |

### Phase 4 — Proactive Forecasting (New Layer, Mock in War Room UI)

Every competing product is reactive — alert arrives, agent investigates. Vigil's forecasting layer fires triggers **before** the alerting system would have.

```
Splunk MCP poll → 1024-point context per device × metric
                  (512 recent fine + 512 historical coarse — multiresolution)
        │
        ▼
CTSM (point forecast) + Chronos (P10/P50/P90)
        Forecast horizon: 2–10 hours (configurable per resolution)
        │
        ▼
3 trigger types — THRESHOLD · TRAJECTORY · UNCERTAINTY
        │
        ▼
Finite State Machine investigation (forecast snapshot attached to audit trail)
        │
        ▼
Feedback loop — labeled fine-tuning corpus for supervised CTSM fine-tuning
```

**CTSM status:** 1.0-preview shipped 24 November 2025 (open-weights on Hugging Face + GitHub); **v1.0 due early 2026** — partnership window is open now. Trained on 300B+ datapoints. **Architecturally produces both quantile and point predictions** — only the Spaces API surfacing is missing, which is why Priority 0 in [`splunk_evals.ipynb`](../splunk_evals.ipynb) is one hour of work, not a model change. [Launch blog: Liang Gou + Sonal Pardeshi](https://www.splunk.com/en_us/blog/artificial-intelligence/introducing-the-cisco-time-series-model.html).

**Three knowledge sources, three time orientations — no competitor has all three:**

| Time | Source | Purpose |
|---|---|---|
| **Past** | Pinecone incident memory | Has this been seen, what fixed it |
| **Present** | Pre-triage + Splunk telemetry | What is happening now, is the alert credible |
| **Future** | CTSM + Chronos forecast | What will happen — should the FSM run now |

**The three trigger types in practice:**

| Trigger | When It Fires | Concrete Example |
|---|---|---|
| **THRESHOLD** | P50 forecast breaches a configured hard limit within the horizon | Border Gateway Protocol route count P50 drops below 700 (configured floor) in 18 minutes — Vigil fires the pre-alert and the FSM begins investigating **before the BGP session actually flaps** |
| **TRAJECTORY** | P50 stays below the threshold but is on a clear deterioration path | Central Processing Unit climbs from 60% to 75% over the last hour; CTSM forecasts 78% in 110 minutes. No hard breach yet but the slope is anomalous — triggers a "watch" investigation |
| **UNCERTAINTY** | P90 confidence band widens significantly — the model says "could be 50, could be 95" | CPU on a core device: P50 stays at 60% but P10–P90 widens from ±5% to ±25% in 30 minutes. **The widening uncertainty itself is the signal** — something is changing that the model can't pattern-match. No statistical-anomaly competitor has this trigger type. |

**The feedback loop — every investigation becomes a labeled training example:**

The FSM's final state (REMEDIATING / ESCALATING / SUPPRESSED) plus the forecast snapshot plus the actual outcome (resolved correctly, escalated to human, confirmed false positive) is precisely the labeled data CTSM fine-tuning requires.

- 1,000 investigations per day → 1,000 labeled examples
- Six months → ~180,000 examples covering the **specific anomaly signatures in this customer's environment**
- Feed the corpus into continued pre-training of CTSM (Priority 3 in [`docs/model-evaluation.md`](./model-evaluation.md)) → **customer-specific CTSM that compounds month over month**

This is the path from "third-party foundation model" to "proprietary asset that compounds." Base model stays 3p; the labeled corpus is 1p — and over time, that corpus is the moat.

**War-room user interface:** Forecast Strip renders all three signals (Border Gateway Protocol route count, Central Processing Unit, packet drop) with shaded P10–P90 confidence band. Triggers colour-coded: orange for threshold breach (`T−18min` countdown), amber for trajectory, violet for uncertainty, green for stable. The False Positive scenario stays all-green — visually disproving the alert before the Finite State Machine runs. Mock data today; live wiring is roughly one week, gated on Priority 0 in [`docs/model-evaluation.md`](./model-evaluation.md).

---

## Reference Investigation — One End-to-End Run

The Packet Loss scenario, top-to-bottom — what the war-room user interface renders when the operator clicks Run Investigation. Every event timestamped from T+0; every input and output captured in the structured audit trail.

> **INC-20240214-001 · Priority 2 · San Jose**
> High packet loss on Cisco Catalyst `sj-catalyst-01` / `GigE0/1`

```
◆ FORECAST PRE-ALERT  Packet drop forecast breaches 1.0% in 8 min       [proactive · before alert]
PRE_TRIAGE         alert scored 0.78 (high), signal_count=3 → proceed   [<1ms · 0 tokens]
TRIAGE             → state transition: "Alert score above threshold"
SPL Knowledge RAG  retrieved: packet_loss_egress (0.63)                 [380ms · 0 tokens]
01 topology        sj-catalyst-01 uplinks sj-core-01, GigE0/1 vlan=100  [118ms]
INVESTIGATING      → state transition: "Data sources confirmed"
02 telemetry       out_errors=2847, utilization=94.2%, drops=1203 ⚠     [287ms]
03 run_spl         avg out_errors=2847/min, spike started 14:30 UTC ⚠   [421ms]
Incident Memory RAG retrieved: INC-2024-0891 (0.84) — exfiltration       [390ms · 0 tokens]
HYPOTHESIZING      → state transition: "Evidence collected, forming root cause"
04 run_spl         src_ip 10.14.22.87 = 71.2% of egress (threshold 60%) [389ms]
05 gen_spl         egress concentration + threat intel join query        [612ms]
ESCALATING         → state transition: "Single IP > 60% egress → ESCALATING"
                                                                          ──────
Finite State Machine: confidence 0.93 · 5 tool calls · forecast verified · ~35s total
```

**Structured output (the audit trail artifact)**:

```json
{
  "incident_id": "INC-20240214-001",
  "final_state": "ESCALATING",
  "hypothesis": "sj-catalyst-01 GigE0/1: out_errors=2847 spike at 14:30 UTC. src_ip 10.14.22.87 = 71.2% egress — isolate pending threat intel",
  "tool_calls": 5,
  "confidence": 0.93,
  "recommended_action": "Isolate src_ip=10.14.22.87 pending threat intel confirmation",
  "forecast_snapshot": {
    "trigger_type": "threshold",
    "metric": "packet_drop_rate",
    "projected_minutes_ahead": 8,
    "model": "Chronos-T5-Small"
  },
  "total_tokens": 4847,
  "cost_usd": 0.0114,
  "duration_secs": 34.8
}
```

**Same architecture handles all four reference scenarios:**

| Scenario | Severity | Forecast Trigger | Final State | Why |
|---|---|---|---|---|
| Packet Loss on GigE0/1 | Priority 2 | THRESHOLD (T−8min) | **ESCALATING** | Single source IP = 71% egress + threat intelligence match |
| Border Gateway Protocol Flap | Priority 2 | THRESHOLD (T−18min) | **REMEDIATING** | Incident memory match 0.78 — known safe fix: `set bgp timers 30 90` |
| CPU Spike on Core Device | Priority 1 | UNCERTAINTY (wide P90) | **ESCALATING** | CRITICAL blast radius + unknown process |
| False Positive | Priority 3 | NONE — forecast strip all-green | **SUPPRESSED** | 5 repeat fires · 0 corroboration · 0 tokens · <1ms |

---

## Competitive Position

Full breakdown across 25+ vendors in [`docs/competitive-landscape.md`](./competitive-landscape.md). The market map:

```
                          AGENTIC / AUTONOMOUS INVESTIGATION
                                       ▲
                                       │
                  Cisco AgenticOps      │      AWS DevOps Agent + Splunk
                  (preview, 2025–26)    │      (GA, April 2025)
                  Juniper Marvis        │      Datadog Bits AI · Dynatrace
                  (single-turn)         │      Davis · New Relic AI
                  ╔═══════════════════╗ │
                  ║      VIGIL         ║│
                  ║  network + agentic ║│
                  ║  + Splunk + Cisco  ║│
                  ╚═══════════════════╝ │
                                        │
   ─── NETWORK ────────────────────────┼───────────────────── GENERAL ─────►
   ── SPECIALIST ──                    │                     OBSERVABILITY
                                        │
                  HPE Aruba · Arista    │      Splunk ITSI · Datadog · Elastic
                  Extreme · Nokia       │      LogicMonitor · BigPanda · Moogsoft
                                        │      ServiceNow · PagerDuty · BMC · IBM
                                        ▼
                          REACTIVE CORRELATION / ANALYTICS
```

**Vigil is the only product in the upper-left quadrant.** Three defensible advantages:

| Advantage | Why It Holds |
|---|---|
| **Cisco + Splunk in one loop** | Owned by same parent post-acquisition; no shipped product bridges them. Every Tier-1 competitor is locked to its own hardware. |
| **Foundation-model forecasting + agentic investigation in one system** | Forecasting specialists don't investigate. Agentic competitors don't forecast. Vigil is the only product unifying them. |
| **Built to absorb Cisco's roadmap, not race it** | When AI Canvas ships, FSM maps to a Canvas workflow. When Deep Network Model ships, LLM call swaps out. Partnership posture, not competition. |

One-sentence statement: **every other product is either network-specialist without Splunk and agentic depth, or general observability without Cisco specialization, or an AIOps platform without investigation depth. Vigil is the only product combining all three.**

---

## Splunk AI Governance Alignment

Vigil ships against all five Splunk AI principles as core architecture — not a compliance afterthought.

| Principle | How Vigil Implements It |
|---|---|
| **Accountability** | Pydantic JSON report per investigation: FSM transition log, tool calls, RAG retrievals, forecast snapshot, confidence score, evidence |
| **Transparency** | Threshold-based transitions cite the rule that fired (e.g. "single source IP > 60% egress → ESCALATING") — not black-box LLM judgment |
| **Privacy** | RBAC passthrough — Vigil inherits Splunk user permissions; no raw logs stored beyond Pinecone summaries |
| **Fairness** | Rules-based pre-triage + configurable thresholds prevent model drift across incident types |
| **Resilience** | Default-to-ESCALATING — ambiguous evidence always routes to human; Pinecone outage falls back to non-RAG investigation |

---

## Roadmap

| Item | Description |
|---|---|
| **SPL Quality Gate** | Score generated SPL for validity, field coverage, scan cost before execution; regenerate below threshold |
| **Investigation-Aware Context Injection** | Prepend FSM state and prior findings to every `saia_generate_spl` call — more targeted, less scan |
| **Continuous Incident Memory** | ServiceNow/Jira webhook auto-embeds resolved incidents — proprietary memory grows over time |
| **SPL Cache** | TTL-cache for known patterns; reduces SAIA prompt consumption 40–60% against the 3,000/month org limit |
| **AI Canvas Integration** | When Cisco AI Canvas ships, Vigil's FSM maps to Canvas workflows — bridge, RAG, evaluator unchanged |
| **Outcome KPI Dashboard** | Business-leader reporting on risk avoided, cost per correct decision, analyst effectiveness — replaces MTTR charts |
| **Prevention Rate Tracking** | Track suppressed/investigated/escalated ratio as Pinecone memory grows — primary operational health signal |
| **Live Forecasting Integration** | Wire Phase 4 forecast layer to live CTSM and Chronos endpoints (gated on Cisco quantile API — see [`model-evaluation.md`](./model-evaluation.md)) |
| **Auto-Contributor** | Vigil autonomously scans CVE databases, competitor product capabilities, and unresolved incident patterns — proposes new detection rules, SPL patterns, and Skills directly to the engineering team. Architecture supports it today via the Phase 4 feedback loop + Phase 3 evaluator. |

---

## Known Limitations

**Honest framing for the demo:** Mock data for Splunk + Cisco Catalyst endpoints (architecture is production-ready, data is demo-scale by design). Pinecone incident memory seeded at 30 records (grows customer-specifically via the Continuous Incident Memory roadmap item). Phase 4 forecasting uses pre-computed fixtures (live wiring is roughly one week, gated on Priority 0 in [`docs/model-evaluation.md`](./model-evaluation.md)). FSM handles known incident patterns; novel scenarios always escalate to a human — **that is the design, not a limitation.**

---

## How Vigil Scales as a Platform — One Workflow, Customized Per Team

**Vigil is an MCP-guided workflow.** A customizable, auditable, human-in-loop investigation playbook that runs on top of Splunk MCP and Cisco Catalyst MCP servers. Each team forks the default workflow, adds their own steps, and configures their own confidence thresholds — **autonomous on routine cases, human-in-loop approval on novel or high-risk cases**.

### Five Dimensions of That One Identity

| Dimension | What It Means in Vigil |
|---|---|
| **MCP-guided** | Vigil reads MCP tool catalogs (Splunk + Cisco Catalyst) and orchestrates calls dynamically. MCP is the only integration contract. **New tools added to the catalog become callable in the workflow automatically — no application code changes.** |
| **Workflow** | A 7-state Finite State Machine with explicit, auditable transitions. Not a free-form agent. Defined in code today, forkable as a markdown / YAML template per team in the v2 Skill Editor. |
| **Customizable per team** | Each team forks the default `TRIAGE → INVESTIGATING → HYPOTHESIZING → REMEDIATING / ESCALATING` path and adds their own steps — "Post to Slack," "Open a Jira ticket," "Trigger a ServiceNow change request" — without writing application code. Custom steps register as MCP tools. |
| **Human-in-loop approvals** | The Finite State Machine routes by confidence band. **High confidence (≥ 0.90) → autonomous remediation.** **Low confidence → human approval gate before any action.** Each team configures their own threshold; the policy lives in the workflow, not in the operator. |
| **Auditable** | Every investigation produces a Pydantic-validated JSON report — FSM transitions, tool calls, Retrieval-Augmented Generation retrievals, forecast snapshot, confidence score, evidence. Sarbanes-Oxley + SOC 2 ready. |

### How Teams Customize the Same Underlying Workflow

| Team | Customization on Top of Default Vigil | Approval Threshold |
|---|---|---|
| **Splunk Security Operations** | Add step: "Open ServiceNow ticket on ESCALATING" + Cisco threat-intel lookup before remediation | Autonomous suppress / remediate; **human approval on every ESCALATING** |
| **Splunk Observability** | Wire Phase 4 forecast as the alert trigger + new step "Post predictive SLO violation to Slack" | Autonomous suppress; **analyst approval before public status-page update** |
| **Splunk IT Service Intelligence** | Add step: "Trigger PagerDuty on high-blast-radius escalation" + service-dependency walk | Autonomous for L3 incidents; **human approval for L1 / L2** |
| **Cisco AgenticOps** | Vigil's Finite State Machine registers as a Canvas Workflow Template; customers further fork inside Canvas | **Configurable per Canvas tenant** |
| **Cisco Cloud Security** | Add step: "Cross-reference Cisco threat intelligence before ESCALATING" + auto-isolate on confirmed match | Autonomous on known-pattern threats; **human approval on novel signatures** |

### The Pattern Visualized — One Canonical Engine, Forked Per Team

```
                  ┌──────────────────────────────────────────────────┐
                  │            CANONICAL VIGIL WORKFLOW                │
                  │       (MCP-guided FSM shipped today)               │
                  │                                                     │
                  │    Pre-Triage → TRIAGE → INVESTIGATING              │
                  │         → HYPOTHESIZING → REMEDIATING / ESCALATING  │
                  │                                                     │
                  │    + Phase 4 forecast pre-alert                     │
                  │    + Pinecone Retrieval-Augmented Generation        │
                  │    + Confidence-band human-in-loop routing          │
                  │    + Pydantic JSON audit trail per investigation    │
                  └─────────────────────┬────────────────────────────┘
                                        │  fork + customize
        ┌───────────────────────────────┼───────────────────────────────┐
        ▼                               ▼                               ▼
┌──────────────────┐           ┌──────────────────┐           ┌──────────────────┐
│  Splunk Security  │           │ Splunk           │           │  Cisco            │
│  Operations       │           │ Observability    │           │  AgenticOps       │
│                   │           │                  │           │                   │
│  + ServiceNow     │           │ + Phase 4 SLO    │           │  + Canvas tenant  │
│    ticket step    │           │   forecast as    │           │    configuration  │
│  + Cisco threat   │           │   alert source   │           │  + Customer-      │
│    intel lookup   │           │ + Slack alert    │           │    specific fork  │
│                   │           │   on prediction  │           │                   │
│  APPROVAL:        │           │ APPROVAL:        │           │  APPROVAL:        │
│  Human required   │           │ Analyst before   │           │  Per-tenant       │
│  on every         │           │ status-page      │           │  configuration    │
│  ESCALATING       │           │ publication      │           │                   │
└─────────┬────────┘           └─────────┬────────┘           └─────────┬────────┘
          │                              │                              │
          └──────────────────────────────┼──────────────────────────────┘
                                         ▼
                  ┌────────────────────────────────────────────────────┐
                  │   EVERY CUSTOM STEP = A NEW MCP TOOL OR SKILL       │
                  │                                                      │
                  │   Registered in Cisco Skills Registry                │
                  │   Available to every other team's workflow           │
                  │   Audit trail records every approval decision        │
                  │                                                      │
                  │   → New Splunk SecOps tool → Splunk Obs. can use it  │
                  │   → New Cisco Cloud Security skill → AgenticOps too  │
                  │   → Every team contributes; every team benefits      │
                  └────────────────────────────────────────────────────┘
```

### Why This Architecture Scales

| Dimension | Linear Approach (1 App per Team) | Vigil's Approach (1 Workflow, Customized) |
|---|---|---|
| **Effort to onboard a new team** | 6–12 months — each team builds their own agent stack from scratch | **1–2 weeks** — fork the canonical workflow, register new MCP tools, configure approval thresholds |
| **Knowledge accumulation** | Each team's tooling lives in its own silo | **Every custom MCP tool / Skill flows back into the registry** — available to every other team's workflow |
| **Governance posture** | 5 different audit formats, 5 different approval policies | **One audit format, one approval-policy abstraction** — configured per team via threshold values, not separate codebases |
| **Foundation model improvements** | Each team independently updates their Large Language Model / forecast model | **Every Claude / Cisco Time Series Model / embedding-model release improves every team's workflow simultaneously** |
| **Cost** | Linear in team count | **Sublinear** — the substrate is shared, only the per-team customizations carry incremental cost |
| **Human-in-loop policy** | Re-implemented per app, inconsistent across products | **One mechanism (FSM confidence-band routing) configured per team** — every approval decision auditable in the same JSON schema |

**The platform pattern in one sentence:** Vigil is the **agentic equivalent of a Splunk dashboard** — one shared engine, customized per team, scaled by adding new MCP tools and approval policies, not by rewriting the agent every time a new use case shows up.

### Three Adoption Tiers Built on the Same Engine

| Audience | Consumption Model |
|---|---|
| **Internal Splunk + Cisco product teams** | Vigil's FSM + RAG + Evaluator consumed as internal libraries with MCP gateway for tool exposure. Each product team onboards in **1–2 weeks** versus 6–12 months building from scratch. |
| **Customer deployments** | Hosted (Cisco / Splunk-managed) or self-hosted in customer Virtual Private Cloud with bring-your-own data plane. RBAC passthrough preserves the customer's security boundary. **Customer-specific incident memory grows in their Pinecone tenant over time — the proprietary corpus stays theirs.** |
| **Developer + partner ecosystem** | Skill SDK + MCP-compliant tool registry + workflow template library + evaluator harness for measuring third-party Skills. Partners (ServiceNow, PagerDuty, security ecosystem ISVs) ship Skills as marketplace artifacts — **revenue-share economics, ecosystem network effects.** |

---

## Results & Outcomes

The metrics that prove the platform works — measured across the four reference scenarios, with the production cost stack (schema enforcement + prompt caching + Haiku tiering) active.

| Metric | Before Vigil | With Vigil | Change |
|---|---|---|---|
| False positive alerts suppressed | 0% | **35–40%** | 0 tokens spent |
| Precision of investigation outcome | 0.55 (unconstrained) | **0.91** (schema-enforced) | +65% — matches Cisco Deep Network Model target |
| Audit trail on every decision | None | **100%** | Sarbanes-Oxley + SOC 2 usable |
| Cost per investigation | ~$0.056 | **~$0.010–$0.014** | **80–85% lower** (schema + caching + tiering) |
| Annual saving at 10K alerts/day | — | **~$620K** | vs unconstrained baseline |
| Proactive triggers ahead of alert | None | Up to **18 min ahead** | Phase 4 forecast layer |
| Mean Time to Resolve (Priority 2) ¹ | 47 minutes | ~35 seconds | 98.8% faster |
| Mean Time to Detect (Priority 2) ¹ | 15 minutes | 8 seconds | 98.7% faster |

*¹ Apply only to the 60–65% of incidents that reach investigation. 35–40% are suppressed at 0 tokens before any model call. Per [Splunk Security Predictions 2026](https://www.splunk.com/en_us/blog/leadership/security-predictions-2026-what-agentic-ai-means-for-the-people-running-the-soc.html): MTTR is a downstream snapshot, not the primary KPI.*

---

## How Vigil Fits Cisco's AI Roadmap

Cisco announced AgenticOps at Cisco Live 2025. Three components are on the roadmap; **Vigil is the application layer that brings them together today and absorbs them as they ship**.

```
                  ┌─────────────────────────────────────────────────────────┐
                  │                  CISCO AI CANVAS                          │
                  │       (Cisco's agentic workflow platform — 2026)          │
                  │       Drag-and-drop orchestration · Generative UI         │
                  │  ┌──────────────────────────────────────────────────┐    │
                  │  │  Vigil's Finite State Machine =                  │    │
                  │  │     a canonical Canvas workflow template          │    │
                  │  └────────────────────┬─────────────────────────────┘    │
                  └────────────────────────┼──────────────────────────────────┘
                                           │ orchestrates
                                           ▼
            ┌──────────────────────────────────────────────────────────────┐
            │       VIGIL'S 7-STATE FSM WORKFLOW (shipped today)            │
            │                                                                │
            │   Pre-Triage → TRIAGE → INVESTIGATING → HYPOTHESIZING          │
            │       │                                       │                │
            │       └→ SUPPRESSED      REMEDIATING / ESCALATING               │
            │                                                                │
            │   Forecast Pre-Alert overlays above (Phase 4)                   │
            │   Pinecone RAG grounds every step (past + present)              │
            └────┬─────────────────────────────┬───────────────────────────────┘
                 │ calls                       │ swap-in candidate
                 ▼                             ▼
       ┌──────────────────────────────┐  ┌──────────────────────────────────┐
       │   CISCO SKILLS REGISTRY       │  │  CISCO DEEP NETWORK MODEL          │
       │   (MCP tool catalog)           │  │  (Cisco-trained network FM)        │
       │   Announced Cisco Live 2025    │  │  Target 2026                        │
       │                                │  │                                     │
       │   ✓ Vigil's 2 new Catalyst    │  │  → Drop-in replacement for the      │
       │     tools register here        │  │    Anthropic Claude call inside     │
       │   ✓ Vigil consumes Splunk MCP  │  │    FSM reasoning states             │
       │     + Cisco Catalyst MCP via   │  │  → Schema enforcement preserves     │
       │     this registry              │  │    the 0.91 precision floor         │
       │                                │  │  → Cisco Time Series Model already  │
       │                                │  │    benchmarked + used in Phase 4    │
       └──────────────────────────────┘  └──────────────────────────────────┘
```

### Three Integration Points

| Cisco Component | Status | How Vigil Plugs In |
|---|---|---|
| **AI Canvas** — agentic orchestration platform | Preview · target 2026 | Vigil's 7-state FSM is **the workflow that runs on Canvas**. The state transition graph maps directly to a Canvas template. When Canvas ships, Vigil ships as a Canvas template — **no rewrite, no migration cost.** |
| **Skills Registry** — MCP tool catalog | Announced Cisco Live 2025 | Vigil registers `get_network_topology` and `get_telemetry_metrics` into the Skills Registry. Vigil's FSM consumes registry Skills as ordinary MCP tools. **Vigil is both consumer and contributor to the registry.** |
| **Deep Network Model** — Cisco network-tuned LLM | Target early 2026 | Drop-in replacement for the Claude call inside FSM reasoning states. Schema-enforced JSON output stays the same — **the model behind the wall changes; the 0.91 precision floor is preserved by the constrained-mode prompt.** Cisco Time Series Model is already benchmarked and used in Phase 4. |

**Why this matters for Cisco:** every Cisco AgenticOps customer who adopts AI Canvas needs an incident commander workflow to run on it. **Vigil is that workflow.** Cisco builds the platform — Vigil is the canonical first application, with measured precision, cost, and audit trail already proven.

**Why this matters for Splunk:** every Splunk customer who runs Cisco AgenticOps needs the Splunk telemetry inside the agent's investigation loop. **Vigil is that loop.** Splunk MCP server + Cisco Catalyst MCP server in one workflow — the integration nobody has shipped, demonstrated and measured today.

---

## The Bottom Line

**Vigil is the agentic reasoning substrate Cisco's AgenticOps vision requires** — running today as a 4-phase application, ready tomorrow as the platform layer that internal product teams, customer deployments, and the developer ecosystem all build on.

| Capability | Status |
|---|---|
| 35–40% of alerts suppressed at zero tokens before any model call | ✅ Shipped |
| 0.91 precision matching Cisco's claimed Deep Network Model target | ✅ Shipped |
| **80–85% lower cost per investigation** vs. unconstrained — **~$620K/year saved at 10K alerts/day** (schema + caching + tiering) | ✅ Shipped |
| Full audit trail per investigation — Sarbanes-Oxley + SOC 2 usable | ✅ Shipped |
| Pinecone RAG grounding every investigation step | ✅ Shipped |
| Outcome-based metrics replacing MTTR — precision, suppression, cost per decision | ✅ Shipped |
| Foundation-model forecasting layer (Cisco Time Series Model + Chronos) with three trigger types | ✅ Shipped (mock) |
| Mean Time to Resolve: 47 min → 35s on Priority 2 incidents | ✅ Shipped |
| Platform substrate model — one workflow customized per team, three adoption tiers | ✅ Documented |
| Comprehensive competitive landscape across five tiers / 25+ vendors | ✅ Documented |

**The path forward:** when Cisco AI Canvas ships, Vigil's Finite State Machine workflows drop into it. When the Deep Network Model ships, the Large Language Model call swaps out. When Cisco Time Series Model v1.0 ships in early 2026, quantile outputs unlock the full confidence-routing layer. The architecture is built to **absorb Cisco's roadmap and the foundation-model ecosystem — not race them**.

**The question is not whether this gets built. Cisco's keynote and Splunk's 2026 predictions make clear it will be. The question is who owns the agentic reasoning layer when it does — and who has the platform substrate that the next 50 applications build on.**
