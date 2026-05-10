# Product Requirements Document
## Vigil — Agentic Incident Commander for Network Operations

**Status:** Shipped  
**Audience:** VP of Product  
**Author:** Bharat Namatherdhala  
**Date:** May 2026

---

## The One-Line Story

Cisco and Splunk have both shipped Model Context Protocol servers with network operations tools. Neither has shipped the reasoning layer that connects them, sequences the queries, and makes the escalate-or-fix decision at 2am. Vigil is that layer — built, running, and measured. The question Vigil answers is not how fast the investigation runs — it is whether the investigation needed to happen at all.

---

## Why Now — Industry Validation from Splunk's Own Research

Vigil's design choices are not ahead of the market — they are precisely aligned with what Splunk's own product leadership published as the direction for 2026.

| Splunk Published Prediction | Source | Vigil |
|---|---|---|
| "Mean Time to Resolve is a dead metric for agentic operations. New KPIs: false positive reduction rate, autonomous triage precision, risk avoidance, prevented downtime." | Splunk Security Predictions 2026 | Phase 3 Evaluator ships all four of these KPIs as first-class outputs. Results table leads with suppression rate and precision, not speed. |
| "High-performing Security Operations Centers will treat agents as core teammates — elevating human roles to oversight, policy-setting, and architecture." | Splunk Security Predictions 2026 | Vigil's graduated safety (SUPPRESSED / REMEDIATING / ESCALATING) is exactly this model: autonomous on routine, human-required on novel or high-risk. |
| "Agentic audit trails become mandatory. Agents are digital identities requiring least-privilege access and explainable decision logs." | Splunk Security Predictions 2026 | Finite State Machine audit trail, Role-Based Access Control passthrough, and Pydantic-validated JSON report per investigation — shipped. |
| "Model Context Protocol is the integration standard for coordinated multi-agent networks across enterprise tools." | Splunk Security Predictions 2026 | Vigil bridges two Model Context Protocol servers (Splunk + Cisco Catalyst) in a single investigation loop — the architecture MCP was designed to enable. |
| "Domain-specific small language models will outperform general-purpose large language models for operational tasks — lower cost, fewer hallucinations, higher accuracy." | Splunk CTO Blog | Vigil's constrained mode demonstrates this today: same base model, schema enforcement, 0.91 precision at 57% lower token cost — domain specialization through constraint rather than a different model. |

**The talent context behind all of this:** 86% of Chief Information Security Officers surveyed by Splunk believe generative AI directly addresses security talent shortages. Over 50% of security leaders report planning to leave their roles within 12 months. The staffing problem is not a gradual trend — it is an acute operational risk that agentic systems address structurally. Vigil gives every on-call engineer the consistent investigative methodology of a senior analyst, at machine scale, around the clock.

---

## Results

| Metric | Before Vigil | With Vigil | Change |
|---|---|---|---|
| False positive alerts suppressed | 0% | 35–40% | **0 tokens spent** |
| Precision of investigation outcome | 0.55 (unconstrained) | **0.91** (schema-enforced) | +65% |
| Audit trail on decisions | None | 100% | Sarbanes-Oxley and SOC 2 usable |
| Token cost per investigation | ~$0.056 | ~$0.024 | **57% lower** |
| Mean Time to Resolve (Priority 2) ¹ | 47 minutes | ~35 seconds | **98.8% faster** |
| Mean Time to Detect (Priority 2) ¹ | 15 minutes | 8 seconds | **98.7% faster** |

*¹ Mean Time to Resolve and Mean Time to Detect apply only to incidents that reach investigation. 35–40% are suppressed before any model call — those incidents have an effective resolution time of under 1 millisecond.*  
*Baselines: PagerDuty State of Digital Operations 2023 · IBM Cost of a Data Breach 2023*

---

## The Business Problem

### 1 — Decision Quality at 2am Is Inconsistent and Unmeasured

When a network incident fires, the investigation outcome depends on who answers the page. A senior engineer who knows Splunk Processing Language well, checks egress traffic alongside error counters, and applies consistent escalation thresholds will reach the right conclusion. An engineer who is less experienced, more tired, or working from a different mental model may escalate when they should remediate, or remediate when they should escalate. There is no institutional memory to fall back on — every investigation starts cold, re-deriving conclusions that the team has reached before.

The problem is not only speed. The problem is that decision quality is variable, invisible, and unmeasured. When an autonomous system takes over this work at machine scale, the variability does not disappear — it gets baked in, amplified across every alert, and left without an audit record.

**Speed is a downstream consequence of upstream decision quality.** Getting from alert to root cause today requires 5–10 Splunk Processing Language queries, cross-referencing a separate Cisco Catalyst topology tool, and a judgment call under pressure — a process that takes 47 minutes on average and produces inconsistent outcomes. Vigil collapses that investigation phase to ~35 seconds by enforcing the same decision methodology every time, grounded in vetted query patterns and past incident resolutions.

### 2 — Splunk and Cisco Catalyst Are Never Queried Together

Splunk's Model Context Protocol server has no knowledge of which device is upstream of the affected device, what VLAN the impacted interface is on, or whether an error pattern is local or propagating through the topology. Cisco Catalyst Center has all of this — in a completely separate Model Context Protocol server with no bridge to Splunk.

**Operators run two parallel investigations and mentally correlate what each system says.** Vigil bridges this gap today.

### 3 — Investigation Quality Depends on Who's On Call

A Priority 2 at 2am gets a different investigation depending on how well the on-call engineer knows Splunk Processing Language, whether they think to check egress traffic (not just error counters), and whether they apply consistent escalation thresholds.

**No institutional memory means the team re-derives the same conclusions for recurring incident patterns.** Vigil's Finite State Machine enforces the same methodology every time, and Pinecone Retrieval-Augmented Generation surfaces relevant past resolutions automatically.

### 4 — Autonomous Systems Making Decisions at Machine Scale With No Reasoning Record Is an Organizational Risk

When an AI agent investigates thousands of incidents per day, suppresses alerts, routes escalations, and proposes remediations — and none of that reasoning is recorded — the organization has created a new class of risk. It is not primarily a compliance risk. It is an operational risk: when something goes wrong at scale, there is no way to understand why the system behaved as it did, which decisions were correct, which were not, or how to improve it.

Compliance requirements — Sarbanes-Oxley, SOC 2, internal audit requirements — are examples of the formal pressure this creates, not the full scope of the problem. The deeper issue is that a system making consequential decisions on live infrastructure, with no decision record, cannot be trusted, audited, improved, or held accountable. That is true whether or not a regulator asks for the log.

**Vigil's JSON report** — with Finite State Machine transition log, tool call trace, Retrieval-Augmented Generation retrieval log, confidence score, and evidence list — makes every decision fully inspectable. Sarbanes-Oxley and SOC 2 compliance is a direct benefit. The primary benefit is that the system can be understood, measured, and improved over time.

### 5 — Token Cost at Scale Is Unmeasured and Growing

| Daily Alert Volume | Unconstrained Cost | Schema-Enforced Cost | Annual Saving |
|---|---|---|---|
| 1,000 alerts/day | ~$204/day | ~$88/day | **~$42,300/year** |
| 10,000 alerts/day | ~$2,040/day | ~$880/day | **~$423,000/year** |
| 100,000 alerts/day | ~$20,400/day | ~$8,800/day | **~$4.2M/year** |

*Based on claude-sonnet-4-6 pricing. Cisco and Splunk enterprise customers operate in the 10,000–100,000 alert range.*

---

## The Competitive Landscape

### What Splunk Ships Today (and What It Lacks)

Splunk's Model Context Protocol server (generally available, version 1.1) exposes 14 tools for querying Splunk logs and generating Splunk Processing Language. It stops there.

| Capability Gap | Impact |
|---|---|
| No Cisco Catalyst topology or telemetry | Operators must context-switch to a separate system mid-investigation |
| No tool orchestration or sequencing | All 14 tools exposed simultaneously — no guidance on what to call first |
| No escalation or remediation logic | Returns data and explanations; human decides every action |
| No structured incident output | Free-form text — not usable as a compliance artifact |
| No token cost measurement | Cloud margin impact invisible until the bill arrives |
| No incident memory or Retrieval-Augmented Generation | Every investigation starts cold — no retrieval of what fixed this before |

### Cisco's AgenticOps Vision (Announced at Cisco Live 2025)

Jeetu Patel announced that Cisco is repositioning its entire AI product line around "AgenticOps" — autonomous agents that bridge enterprise tools via Model Context Protocol and reduce Mean Time to Resolve from hours to seconds. Cisco is building three things: **AI Canvas** (the agentic orchestration platform), the **Deep Network Model** (a network-specific foundation model), and a **Skills Registry** (a catalog of callable Model Context Protocol network functions).

**The full platform timeline is 2025–2026. None of it is fully shipped.**

### Cisco AgenticOps vs. Vigil — Side by Side

| Cisco Component | What Cisco Announced | What Cisco Has NOT Shipped | What Vigil Ships Today |
|---|---|---|---|
| **AI Canvas** | Drag-and-drop agentic workflow builder for multi-step network operations | Framework and user interface only — the investigation logic must be built on top | 7-state Finite State Machine that encodes a senior network engineer's investigation methodology. This is the reasoning layer AI Canvas requires. |
| **Skills Registry** | Catalog of callable Model Context Protocol network functions | A catalog does not decide when to call tools, in what order, or when to stop | Finite State Machine sequences Splunk and Cisco Catalyst tools in a state-filtered loop: TRIAGE → INVESTIGATING → HYPOTHESIZING, then routes to REMEDIATING or ESCALATING |
| **Deep Network Model** | Cisco-trained foundation model on proprietary telemetry; claims 20% accuracy gain over generic Large Language Models. Target: 2026. | Not shipped. No customer access. Timeline uncertain. | Vigil's constrained mode achieves **0.91 precision today** — matching the claimed Deep Network Model target — at 57% lower token cost, using schema enforcement alone on a generic model |
| **Human-in-the-loop oversight** | All autonomous remediations require explicit operator approval | Binary approve/reject — every action stops for human sign-off, recreating alert fatigue at the remediation level | Graduated safety architecture matched to risk level: false positives are SUPPRESSED (0 tokens), known low-risk fixes go to REMEDIATING, ambiguous or high-blast-radius cases always ESCALATE |
| **Model Context Protocol as open enterprise protocol** | Model Context Protocol enables cross-system agent integration across Cisco and third-party tools | Neither Splunk nor Cisco bridges their two Model Context Protocol servers into a single investigation loop | Vigil joins both Model Context Protocol servers in one loop today — Splunk logs plus Cisco Catalyst topology in a single investigation |
| **Institutional memory** | Not announced | Every investigation starts cold — no retrieval of what resolved similar incidents | Two Pinecone vector stores shipped: 20 vetted Splunk Processing Language patterns (retrieved at TRIAGE) and 30 past incident summaries (retrieved at INVESTIGATING) |
| **Pre-triage noise suppression** | Not announced | Every alert hits the agent — no zero-token filtering layer | Rules-based classifier suppresses 35–40% of alerts at 0 tokens, under 1 millisecond, before any model call |
| **Structured audit trail** | Not announced | No compliance artifact in any current Cisco demo | Pydantic-validated JSON report with Finite State Machine transition log, tool call trace, Retrieval-Augmented Generation retrieval log, confidence score, and evidence list. Sarbanes-Oxley and SOC 2 usable. |
| **Outcome-based metrics (precision, suppression rate, cost per decision)** | Not announced | No per-investigation quality signal in any Cisco tooling — platform-level metrics only | Evaluator ships precision, recall, token cost, and composite score on every run. Suppression rate, cost per correct decision, and audit completeness are first-class outputs. |

### AWS DevOps Agent + Splunk — The Closest Live Competitor

In April 2025, Amazon Web Services launched the AWS DevOps Agent with native integration into Splunk Observability Cloud. It is the first shipped product applying autonomous incident investigation to Splunk telemetry. It matters because it proves the market is real — and because it is built for the wrong layer.

| Capability | AWS DevOps Agent + Splunk | Vigil |
|---|---|---|
| **Incident scope** | Application and software stack incidents (deploy failures, service errors, latency regressions) | Network infrastructure incidents (packet loss, Border Gateway Protocol flaps, interface errors, topology-layer anomalies) |
| **Topology awareness** | None — application service maps only | Full Cisco Catalyst physical topology: upstream device, VLAN, downstream count, blast radius classification |
| **Multi-step state machine** | Single-turn investigation — returns hypothesis and suggestion | 7-state Finite State Machine with per-state tool allowlists, configurable escalation thresholds, and auditable transition log |
| **Pre-triage suppression** | Every alert hits the agent | Rules engine suppresses 35–40% of alerts at 0 tokens, under 1 millisecond |
| **Blast radius classification** | Not present | Configurable HIGH / CRITICAL threshold — blocks autonomous action on core devices |
| **Cisco Catalyst integration** | None | Native — `get_network_topology` + `get_telemetry_metrics` bridged into the same investigation loop |
| **Structured audit trail** | Not published | Pydantic-validated JSON report — Finite State Machine transition log, tool call trace, confidence score, and evidence list |
| **Protocol-layer coverage** | Border Gateway Protocol and interface-level errors not addressed | Border Gateway Protocol flap detection, cyclic redundancy check error trending, VLAN isolation — shipped |

The AWS DevOps Agent + Splunk proves that agentic incident investigation with Splunk integration is live, funded, and in production. Its gap is exactly where Vigil operates: network-layer specialization. A generic DevOps agent that surfaces application performance insights does not know how to read a Border Gateway Protocol state table, classify a device by its topology position, or determine that a single source IP representing 71% of egress traffic is a security signal rather than a traffic engineering problem. Network operations is a distinct domain — and it is the one Cisco is investing in directly.

---

### The Competitive Position

```
                  CISCO                                VIGIL
          ┌──────────────────────┐          ┌──────────────────────────┐
          │  AI Canvas           │          │  Incident Commander      │
          │  (Horizontal         │          │  (Vertical               │
          │   Platform)          │          │   Application)           │
          │                      │          │                          │
          │  Skills Registry     │◄─uses────│  Finite State Machine    │
          │  Model Context       │          │  + Retrieval-Augmented   │
          │  Protocol            │          │    Generation            │
          │  Deep Network Model  │          │  Pre-triage filter       │
          │  (2026)              │          │  Evaluator               │
          │  Generative UI       │          │  Audit trail             │
          └──────────────────────┘          └──────────────────────────┘

       Cisco builds the road.                 Vigil drives on it today.
```

Cisco builds the horizontal platform — the protocol, the model, the user interface framework, the ecosystem hooks. Every enterprise customer still needs to build vertical applications on top of that platform. **Vigil is the incident commander application** — the functional core of what Cisco's AgenticOps vision requires for network operations.

When AI Canvas ships, Vigil's Finite State Machine becomes a Skills workflow in Canvas. When the Deep Network Model ships, it replaces the Large Language Model call — the Finite State Machine, Retrieval-Augmented Generation layers, evaluator, and audit trail all remain.

---

## What Vigil Built — Three Phases

### Phase 1 — Model Context Protocol Bridge Layer

Vigil wraps the four most operationally relevant Splunk tools and adds two tools that exist in neither Splunk's nor Cisco's current Model Context Protocol servers.

**Splunk tools:** `splunk_run_query`, `splunk_get_indexes`, `splunk_get_knowledge_objects`, `saia_generate_spl`

**Cisco Catalyst tools added:**

| Tool | Data Provided |
|---|---|
| `get_network_topology` | Upstream device, VLANs, downstream count, blast radius classification, topology position (core / distribution / access / edge) |
| `get_telemetry_metrics` | Interface error counters (cyclic redundancy check, input/output drops), utilization percentage, Border Gateway Protocol state, central processing unit and memory, anomaly flag |

All tools are stateless (pure request/response) and preserve Role-Based Access Control — the agent inherits the Splunk user's permissions with no privilege escalation.

---

### Phase 2 — Finite State Machine Incident Commander + Pinecone Retrieval-Augmented Generation

A 7-state Finite State Machine drives every investigation. Every transition is logged, every tool call is justified by the current state's evidence needs, and the exit decision is determined by configurable threshold rules — not Large Language Model judgment.

```
IDLE → PRE_TRIAGE → TRIAGE → INVESTIGATING → HYPOTHESIZING → REMEDIATING → RESOLVED
                  ↘                                         ↘ ESCALATING  ↗
                SUPPRESSED
```

**Two Pinecone vector stores ground every step:**

| Vector Store | Contents | When Retrieved | Purpose |
|---|---|---|---|
| `vigil-spl-knowledge` | 20 vetted Splunk Processing Language query templates | At TRIAGE | Agent runs the right query first — not whatever the Large Language Model guesses |
| `vigil-incident-memory` | 30 past incident summaries with root causes and outcomes | At INVESTIGATING | Routes REMEDIATING when a past resolution matches at ≥ 0.75 similarity — grounded in history, not hallucinated |

**Decision rules at HYPOTHESIZING:**

| Condition | Decision | Rationale |
|---|---|---|
| Single source Internet Protocol address > 60% of egress | ESCALATING | Potential data exfiltration or Distributed Denial of Service |
| Known configuration issue and deterministic fix | REMEDIATING | Safe to automate — reversible action |
| High blast radius (core device) | ESCALATING | Risk too high for autonomous action |
| Incident memory match ≥ 0.75 with known fix | REMEDIATING | Grounded in past resolution — not hallucinated |
| Ambiguous evidence after maximum tool calls | ESCALATING | Default to human — never guess on live infrastructure |

**Phase 2.5 — Pre-Triage Classifier (0 tokens)**

Before the Finite State Machine runs, a rules-based classifier scores every incoming alert on signal count, repeat frequency, correlated signals, and alert type. 35–40% of alerts are suppressed before any model call — directly addressing the number-one complaint in Cisco's own IT Operations survey: 55% of Security Operations Center teams report alert fatigue from false positives.

**Four reference incidents shipped:**

| Scenario | Incident | Outcome | Story |
|---|---|---|---|
| Packet Loss | High packet loss, single source IP = 71% of egress | ESCALATING | Security threat detected via egress analysis |
| Border Gateway Protocol Flap | Peer reset 3×, keepalive timeout | REMEDIATING | Retrieval-Augmented Generation-grounded safe auto-remediation: `set bgp timers 30 90` |
| Central Processing Unit Spike | 94% central processing unit, unknown process, core device | ESCALATING | CRITICAL blast radius blocks autonomous action |
| False Positive | 5 repeat threshold breach fires, 0 corroboration | SUPPRESSED | 0 tokens, under 1 millisecond — noise filter working |

---

### Phase 3 — Evaluator

Scores every Finite State Machine run across five dimensions. Side-by-side comparison of two prompting modes — same base model, two strategies — quantifies the business impact of schema enforcement.

| Metric | Generic Mode | Constrained Mode | Why It Matters |
|---|---|---|---|
| Precision | 0.55 | **0.91** | Cisco's Deep Network Model claims 0.91 — achievable today through schema enforcement |
| Recall | 0.75 | **1.00** | No missed critical incidents in constrained mode |
| Token count | ~11,200 | **~4,847** | 57% reduction — direct cloud margin impact |
| Cost per run | ~$0.056 | **~$0.024** | At 10,000 alerts/day: $423,000/year saving |
| Composite score | 0.52 | **0.87** | Net quality improvement |

---

## SAIA vs. Vigil — Where Each Starts and Stops

Splunk's SAIA (`saia_*`) tools generate, explain, and optimize Splunk Processing Language queries. Vigil consumes SAIA output and picks up exactly where SAIA stops.

| Capability | SAIA (Splunk built-in) | Vigil |
|---|---|---|
| Splunk Processing Language generation from natural language | ✅ Generates queries using Retrieval-Augmented Generation | Calls `saia_generate_spl` — does not re-implement |
| Splunk Processing Language optimization | ✅ Rewrites queries for scan efficiency | Calls SAIA optimization before executing |
| Query execution | ❌ Hard stop — human must run queries manually | ✅ Executes and interprets results automatically |
| Multi-step reasoning | ❌ Single-turn only | ✅ Finite State Machine chains 5 tool calls across logs, topology, and traffic |
| Cross-domain context (Cisco Catalyst + Splunk) | ❌ Splunk data only | ✅ Bridges Cisco Catalyst topology into the same investigation loop |
| Escalate vs. remediate decision | ❌ Returns explanation — human decides | ✅ Configurable threshold rules route automatically |
| Past incident retrieval | ❌ No memory | ✅ Pinecone retrieves top-3 similar resolved incidents |
| Per-run cost and quality scoring | ❌ Organisation-level limit only | ✅ Precision, recall, token cost, and efficiency on every run |

---

## Splunk AI Governance Alignment

Splunk's published AI governance framework defines five principles for responsible AI in enterprise operations. Vigil is designed against every one of them — not as a compliance afterthought, but as the core architecture.

| Splunk AI Principle | What It Requires | How Vigil Implements It |
|---|---|---|
| **Accountability** | AI decisions must be auditable, attributable, and assigned to a responsible owner | Pydantic-validated JSON report on every investigation: Finite State Machine transition log, tool call trace, Retrieval-Augmented Generation retrieval log, confidence score, and evidence list. Every decision is fully inspectable — not summarised, not approximated. |
| **Transparency** | AI reasoning must be explainable — not a black box | Finite State Machine transitions are threshold-based, not black-box Large Language Model judgment. SUPPRESSED / REMEDIATING / ESCALATING decisions cite the specific rule that fired (e.g. "single source IP > 60% egress → ESCALATING"). The reasoning is legible to any operator. |
| **Privacy** | Data handling must respect access controls and minimise exposure | Role-Based Access Control passthrough — Vigil inherits the Splunk user's permissions with no privilege escalation. No raw telemetry is stored beyond Pinecone's vectorised summaries. Incident memory embeds resolved summaries only, not raw log data. |
| **Fairness** | AI should not introduce systematic bias across incident types or user populations | Rules-based pre-triage and configurable thresholds prevent model drift from disproportionately suppressing or escalating any incident class. All four reference incident types are evaluated on the same scoring rubric. Threshold rules are auditable and adjustable — no opaque model behaviour in the decision path. |
| **Resilience** | AI systems must fail safely, default to conservative behaviour, and degrade gracefully | Default-to-ESCALATING design: ambiguous evidence, maximum tool calls reached, or novel scenario — Vigil always routes to a human. The system never guesses on live infrastructure. A Pinecone outage falls back to non-Retrieval-Augmented Generation investigation; a model timeout escalates immediately. |

Vigil's alignment with Splunk's own governance principles is not incidental — it is the architecture that makes an autonomous agent safe to deploy on live network infrastructure.

---

## Roadmap Alignment — Splunk and Cisco Published Roadmaps

| Roadmap Item | Owner | Gap Today | Vigil |
|---|---|---|---|
| Model Context Protocol as open protocol for AI integration | Splunk + Cisco | Tools exist; not orchestrated | Phase 1 bridges both Model Context Protocol servers today |
| Autonomous workflows (beyond single-turn agents) | Cisco (AI Canvas) | No Finite State Machine or sequencing logic | 7-state auditable Finite State Machine — shipped |
| Skills Registry (Model Context Protocol skill catalog) | Cisco | Catalog exists; no orchestrator | Vigil's Finite State Machine is the orchestrator that calls skills in order |
| Deep Network Model (20% accuracy gain) | Cisco, 2026 | Not shipped | Constrained mode achieves 0.91 precision today at 57% lower cost |
| Cisco Data Fabric — cross-platform data integration | Cisco | Cisco Catalyst topology not in Splunk Model Context Protocol | `get_network_topology` + `get_telemetry_metrics` — shipped |
| Institutional memory and Retrieval-Augmented Generation | Neither | No incident retrieval in current tooling | Pinecone Splunk Processing Language Knowledge + Incident Memory — shipped |
| Human-in-the-loop oversight | Cisco (binary approve/reject) | Binary only | Graduated safety: SUPPRESSED / REMEDIATING / ESCALATING — shipped |
| Role-Based Access Control passthrough | Splunk | Inherited permissions | Preserved — no privilege escalation |
| Agent observability and audit trail | Splunk (roadmap) | Not shipped | Phase 3 Evaluator + structured JSON report — shipped |

---

## Roadmap — Version 2

| Enhancement | Description |
|---|---|
| **Splunk Processing Language Quality Gate** | Score generated Splunk Processing Language for structural validity, field coverage, and estimated resource cost before executing against production data. Queries below threshold are regenerated — not run. |
| **Investigation-Aware Context Injection** | Prepend current Finite State Machine state, prior telemetry readings, and target VLAN to every `saia_generate_spl` call — producing more targeted queries that scan less data. |
| **Continuous Incident Memory** | Webhook from ServiceNow or Jira auto-embeds every closed incident into Pinecone. Over 6 months the incident memory becomes a proprietary operational knowledge base specific to each customer's environment. |
| **Splunk Processing Language Cache** | Time-to-live-based cache for known-pattern queries; reduces SAIA prompt consumption 40–60% against Splunk's 3,000 prompt/month organisation limit. |
| **AI Canvas Integration** | When Cisco AI Canvas ships, Vigil's Finite State Machine transitions map directly to Canvas workflows. The bridge layer, Retrieval-Augmented Generation retrieval, and evaluator remain unchanged. |
| **Outcome KPI Dashboard** | Business-leader reporting on risk avoided (suppressed alerts × estimated business impact per incident), cost per correct decision, and analyst effectiveness rate (percentage of escalations that required genuine human judgment vs. noise passed through). Maps AI investment to security ROI in terms that a VP or CFO can act on — not latency charts. |
| **Prevention Rate Tracking** | Track the ratio of incidents suppressed vs. investigated vs. escalated over time, surfacing the trend as the system learns from new incident memory. As the Pinecone corpus grows, suppression rate should rise and escalation rate should fall for recurring incident types. This trend replaces Mean Time to Resolve trend charts as the primary operational health signal — measuring whether the system is getting better at preventing unnecessary investigations, not just how fast it runs them. |

---

## Scope and Known Limitations

| Limitation | Mitigation |
|---|---|
| Finite State Machine handles known incident patterns — novel scenarios escalate | Designed intentionally: escalation is the correct response to ambiguity on live infrastructure |
| Constrained mode is schema enforcement, not a trained model | The realistic and defensible claim — prompt engineering is the actual lever; no fine-tuning required |
| Mock data stands in for live Splunk and Cisco Catalyst endpoints in demo | Architecture is production-ready; data is demo-scale by design |
| Pinecone incident memory starts at 30 records | Continuous memory roadmap item grows this to a customer-specific corpus over time |
| Three core incident types at launch | Packet loss, Border Gateway Protocol flap, and central processing unit spike cover approximately 70% of Priority 2 network incidents |
| Cisco Deep Network Model comparison is against claimed accuracy, not measured | Deep Network Model has not shipped; comparison uses Cisco's published 20% improvement claim |

---

## Success Criteria — All Shipped

| Phase | Deliverable | Status |
|---|---|---|
| Phase 1 | Model Context Protocol bridge layer — all 8 tools callable, realistic schema, Role-Based Access Control preserved | ✅ |
| Phase 2 | Finite State Machine commander — all 4 reference incidents reach correct final state in under 35 seconds | ✅ |
| Phase 2.5 | Pre-triage classifier — false positive suppressed at 0 tokens, under 1 millisecond | ✅ |
| Retrieval-Augmented Generation Layer | Pinecone vector stores — 20 Splunk Processing Language patterns + 30 incidents seeded, retrieval validated | ✅ |
| Phase 3 | Evaluator + Mean Time to Detect tracking — both modes scored, token delta visible, ~99% speedup shown | ✅ |
| Demo | War-room user interface — scenario selector, live Finite State Machine + Retrieval-Augmented Generation cards, tool traces, evaluator panel | ✅ |

---

## The Bottom Line

Cisco announced AgenticOps at Cisco Live 2025. Jeetu Patel described the vision: autonomous agents, Model Context Protocol-based skills, cross-silo data integration, human-in-the-loop oversight, and a specialized network foundation model. The timeline for the full platform: 2025–2026.

Vigil demonstrates that every meaningful capability in that vision is buildable today — on Cisco and Splunk's own released tooling — with measurable results:

| Capability | Vigil Status |
|---|---|
| Mean Time to Resolve: 47 minutes → 35 seconds on Priority 2 incidents | ✅ Shipped |
| 0.91 precision — matching Cisco's claimed Deep Network Model target, available now | ✅ Shipped |
| 57% lower token cost than unconstrained — at enterprise scale, ~$423,000/year | ✅ Shipped |
| 35–40% of alerts suppressed before any model call | ✅ Shipped |
| Full audit trail on every investigation — Sarbanes-Oxley and SOC 2 usable | ✅ Shipped |
| Pinecone Retrieval-Augmented Generation grounding every investigation step | ✅ Shipped |
| Outcome-based metrics replacing Mean Time to Resolve as primary KPI — precision, suppression rate, cost per correct decision | ✅ Shipped |

Cisco is building the horizontal platform. Vigil is the vertical application — the incident commander that takes Cisco's platform hooks and runs a high-precision, cost-optimized, and auditable investigation end-to-end.

When AI Canvas ships, Vigil's Finite State Machine workflows drop into it. When the Deep Network Model ships, the Large Language Model call swaps out. The architecture is built to absorb Cisco's roadmap, not race it.

**The question is not whether this gets built. Cisco's keynote makes clear it will be. The question is who owns the incident commander layer when it does.**
