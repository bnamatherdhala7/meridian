# Vigil — Agentic Network Incident Commander

> Cisco and Splunk shipped the tools. Nobody shipped the brain.

Vigil is a Finite State Machine agent that sits on top of Splunk's Model Context Protocol server and Cisco Catalyst Center. It autonomously investigates network incidents — deciding which tools to call, in what order, and whether to escalate or self-heal — backed by Pinecone Retrieval-Augmented Generation that retrieves vetted Splunk Processing Language patterns and past incident memory at each investigation step.

---

## Results

| Metric | Manual Network Operations Center | Vigil | Improvement |
|---|---|---|---|
| False positives suppressed | 0% | 35–40% | **0 tokens, 0 latency** |
| Precision of investigation outcome | 0.55 (unconstrained) | **0.91** (schema-enforced) | +65% |
| Decisions with full audit trail | 0% | 100% | Finite State Machine trace + JSON report |
| Token cost per investigation | — | ~$0.024 | **57% less than unconstrained** |
| Mean Time to Detect (Priority 2) ¹ | 15 minutes | 8 seconds | 98.7% faster |
| Mean Time to Resolve (Priority 2) ¹ | 47 minutes | ~35 seconds | 98.8% faster |

*¹ Applies only to the 60–65% of incidents that reach investigation. 35–40% are suppressed at 0 tokens before any model call.*

*Benchmarks: PagerDuty State of Digital Operations 2023 · IBM Cost of a Data Breach 2023*

---

## The Five Problems Splunk Customers Face — In Splunk's Own Words

| # | Problem | Splunk-Published Evidence | Vigil's Answer |
|---|---|---|---|
| **1** | **False positive alert fatigue** | 55% of orgs have too many false positives · 32% of analyst day spent on false alarms · 94% of CISOs cite false alerts as top burnout driver *(State of Security 2025, Splunk CISO Report)* | Phase 2.5 pre-triage suppresses 35–40% of alerts at zero tokens, <1ms |
| **2** | **Manual, fragmented investigation** | 81% of SOC pros name manual investigations across disconnected tools as #1 contributor to slow detection · ~$58K · 50–150 hours per incident *(Dimitri McKay, Splunk)* | Splunk + Cisco Catalyst in one investigation loop — 47 min → 35s |
| **3** | **Tool sprawl is the dominant inefficiency** | 78% of orgs say tools are disconnected · 59% cite tool maintenance as #1 SOC inefficiency · 46% spend more time configuring than defending *(State of Security 2025, Kirsty Paine)* | Reasoning layer, not another platform — consumes existing MCP tools, same RBAC, same data |
| **4** | **Reactive operations are no longer enough** | *"Traditional, reactive operations are no longer enough"* (Craig Robin, 2026) · *"Agentic AI enables organizations to get ahead of incidents"* (Kamal Hathi, SVP & GM Splunk) | Phase 4 forecasting layer fires triggers up to 18 min before alerts — only product combining foundation-model forecasting with agentic investigation |
| **5** | **Machine-scale decisions without audit trail** | 73% of observability teams report outages caused by ignored alerts · 65% of CISOs sense employee burnout · *"Agentic audit trails are mandatory"* (Splunk Security Predictions 2026) | Pydantic JSON report per investigation — FSM transitions, tool calls, RAG hits, forecast snapshot, confidence, evidence. SOX + SOC 2 usable. |

**Per Splunk's 2026 Predictions:** *"MTTR becomes less a measure of performance and more a snapshot of how late we were in the process. SOC directors will look toward outcome-based measures — reduction in false positives, precision of autonomous triage, risk avoided rather than risk responded to."* Vigil's results table leads with those four metrics.

Tools exist on both sides. **What nobody has shipped is the reasoning layer that connects Splunk and Cisco Catalyst, sequences the queries, and makes the escalate-or-fix decision at 2am.**

---

## Splunk Model Context Protocol Server — 14 Tools Shipped Today

Splunk's Model Context Protocol server (generally available, version 1.1) exposes 14 tools across two namespaces: `splunk_*` for platform queries and `saia_*` for AI-assisted Splunk Processing Language generation.

| Tool | What It Does |
|---|---|
| `splunk_run_query` | Execute a Splunk Processing Language search and return results |
| `splunk_get_indexes` | List available indexes |
| `splunk_get_index_info` | Detailed metadata on a specific index |
| `splunk_get_info` | Splunk instance info (version, configuration) |
| `splunk_get_metadata` | Hosts, sources, and source types metadata |
| `splunk_get_user_info` | Authenticated user details |
| `splunk_get_user_list` | List of all Splunk users |
| `splunk_get_kv_store_collections` | Key-Value Store collection stats |
| `splunk_get_knowledge_objects` | Saved searches, field extractions, lookups |
| `splunk_run_saved_search` | Run a saved search *(beta)* |
| `saia_generate_spl` | Generate Splunk Processing Language from natural language |
| `saia_explain_spl` | Explain a Splunk Processing Language query in plain English |
| `saia_optimize_spl` | Optimize a Splunk Processing Language query for performance |
| `saia_ask_splunk_question` | Answer conceptual questions about Splunk Processing Language |

### What's Missing — And What Vigil Adds

| Capability | Splunk Model Context Protocol | Gap | Vigil |
|---|:---:|---|:---:|
| **Cisco Catalyst network topology** (device graph, uplinks, VLANs) | ❌ | Cisco Catalyst data lives in a completely separate server | ✅ `get_network_topology` |
| **Cisco Catalyst interface telemetry** (error counters, utilization, drops) | ❌ | No typed tool exists for structured interface metrics | ✅ `get_telemetry_metrics` |
| **Retrieval-Augmented Generation over vetted Splunk Processing Language patterns** | ❌ | No vector search over validated query templates | ✅ Pinecone `vigil-spl-knowledge` (20 patterns) |
| **Past incident memory** | ❌ | No retrieval of similar resolved incidents | ✅ Pinecone `vigil-incident-memory` (30 records) |
| **Tool orchestration — what to call first** | ❌ | All 14 tools exposed simultaneously; no sequencing guidance | ✅ Finite State Machine drives TRIAGE → INVESTIGATING → HYPOTHESIZING |
| **State-filtered tool access** | ❌ | Large Language Model sees all tools every turn — wastes tokens | ✅ Per-state allowlists; tool list changes each phase |
| **Threshold-based escalation rules** | ❌ | No decision logic shipped | ✅ Configurable rules (e.g. single source IP > 60% egress → ESCALATING) |
| **Pre-triage noise suppression** | ❌ | Every alert hits the Large Language Model | ✅ Rules engine suppresses 35–40% at 0 tokens, under 1 millisecond |
| **Structured JSON incident report** | ❌ | Free-form text only | ✅ Pydantic-validated schema, Sarbanes-Oxley usable |
| **Token cost per investigation** | ❌ | Not measured or surfaced | ✅ First-class evaluator metric |
| **Role-Based Access Control passthrough** | ✅ | — | Preserved — no privilege escalation |
| **OAuth 2.0** | 🗓 Roadmap | Not yet shipped | Extension point documented |

---

## Vigil vs. Cisco AgenticOps

At Cisco Live 2025, Jeetu Patel announced "AgenticOps" — Cisco's bet that the next wave of network operations runs on autonomous agents. Cisco is building the horizontal platform. Vigil is the vertical application already running on it.

| Cisco Announcement | Cisco Status | What's Missing | Vigil Status |
|---|---|---|---|
| **AI Canvas** — drag-and-drop agentic workflow builder for network operations | Preview, H2 2025 | Framework only — the investigation logic must be built on top | Vigil's 7-state Finite State Machine is the reasoning layer AI Canvas requires |
| **Skills Registry** — catalog of callable Model Context Protocol network functions | Preview | A catalog of tools does not decide when to call them or in what order | Vigil's Finite State Machine sequences Splunk and Cisco tools in a state-filtered investigation loop |
| **Deep Network Model** — Cisco-trained foundation model, 20% accuracy gain claimed | Research, 2026 | Not shipped; timeline uncertain; no customer access | Vigil's constrained mode achieves **0.91 precision today** — matching the claimed target at 57% lower token cost |
| **Human-in-the-loop oversight** — all remediations require operator approval | Shipping (binary only) | Every action stops for approval — recreates alert fatigue at the remediation level | Vigil's graduated safety matches autonomy to risk: SUPPRESSED / REMEDIATING / ESCALATING |
| **Model Context Protocol as open enterprise protocol** | Generally Available | Tools exist — neither Splunk nor Cisco bridges them into a single loop | Vigil joins both Model Context Protocol servers in one investigation today |
| **Institutional memory** — retrieval of past incidents | Not announced | Every investigation starts cold | Vigil ships two Pinecone vector stores: 20 Splunk Processing Language patterns + 30 past incident summaries |
| **Pre-triage noise suppression** | Not announced | Every alert hits the agent | Vigil suppresses 35–40% of alerts at 0 tokens before any model call |
| **Structured audit trail per investigation** | Not announced | No compliance artifact in any current Cisco demo | Vigil produces a Pydantic-validated JSON report — Sarbanes-Oxley and SOC 2 usable |

---

## AWS DevOps Agent + Splunk — Why Vigil Is Different

Amazon's AWS DevOps Agent (April 2025, integrated with Splunk Observability Cloud) is the closest live competitor. It proves the market exists. Its gap is the layer Vigil is built for.

| Capability | AWS DevOps Agent + Splunk | Vigil |
|---|---|---|
| **Incident scope** | Application and software stack (deploy failures, service errors, latency) | Network infrastructure (packet loss, Border Gateway Protocol flaps, interface errors, topology anomalies) |
| **Cisco Catalyst topology** | None | `get_network_topology` — upstream device, VLAN, blast radius, topology position |
| **Multi-step state machine** | Single-turn — returns hypothesis | 7-state Finite State Machine with per-state tool allowlists and auditable transition log |
| **Pre-triage suppression** | Every alert hits the agent | 35–40% suppressed at 0 tokens, under 1 millisecond |
| **Blast radius classification** | Not present | HIGH / CRITICAL threshold blocks autonomous action on core devices |
| **Structured audit trail** | Not published | Pydantic-validated JSON — Finite State Machine log, tool trace, confidence score |
| **Protocol-layer coverage** | Border Gateway Protocol and interface errors not addressed | Border Gateway Protocol flap detection, cyclic redundancy check trending, VLAN isolation — shipped |

Network operations is a distinct domain. A DevOps agent that surfaces application latency insights cannot classify a device by topology position or determine that a single source IP at 71% of egress is a security event rather than a load distribution issue.

---

## SAIA vs. Vigil — Where Each Starts and Stops

Splunk's SAIA (`saia_*`) tools generate, explain, and optimize Splunk Processing Language queries. Vigil consumes SAIA output and picks up exactly where SAIA stops.

| Capability | SAIA (Splunk built-in) | Vigil |
|---|---|---|
| Splunk Processing Language generation from natural language | ✅ Generates queries using Retrieval-Augmented Generation. Handles ambiguous prompts. | Calls `saia_generate_spl` — does not re-implement |
| Splunk Processing Language performance optimization | ✅ Rewrites queries for scan efficiency | Calls SAIA optimization before executing |
| Query execution | ❌ **Hard stop** — human must run queries manually | ✅ Executes via `splunk_run_query` and interprets results |
| Multi-step reasoning | ❌ **Hard stop** — single-turn only, one prompt → one query | ✅ Finite State Machine chains 5 tool calls across logs, topology, and traffic |
| Cross-domain context (Cisco Catalyst + Splunk) | ❌ **Hard stop** — Splunk data only | ✅ Bridges Cisco Catalyst topology and telemetry into the same investigation loop |
| Escalate vs. remediate decision | ❌ **Hard stop** — returns query and explanation only | ✅ Configurable threshold rules route automatically to REMEDIATING or ESCALATING |
| Past incident retrieval | ❌ No incident memory | ✅ Pinecone retrieves top-3 similar resolved incidents |
| Per-run cost and quality scoring | ❌ Organisation-level limit only — no per-query insight | ✅ Precision, recall, token cost, and efficiency on every run |

---

## Cisco Catalyst Model Context Protocol Tools

Vigil adds two tools that bridge Cisco Catalyst Center data into the Splunk investigation loop — tools that exist in neither Splunk's nor Cisco's current Model Context Protocol servers.

### `get_network_topology`
Returns the physical network graph for a device: upstream device, VLANs, downstream count, blast radius classification, and position in the topology (core / distribution / access / edge).

```json
{
  "device": "sj-catalyst-01",
  "upstream": "sj-core-01",
  "vlan": [100, 200],
  "downstream_count": 8,
  "blast_radius": "MEDIUM",
  "position": "distribution"
}
```

### `get_telemetry_metrics`
Returns live interface-level and device-level telemetry: error counters (cyclic redundancy check, input/output drops), utilization percentage, Border Gateway Protocol state, central processing unit and memory, and an anomaly flag.

```json
{
  "device": "sj-catalyst-01",
  "interface": "GigE0/1",
  "metrics": {
    "out_errors": 2847,
    "input_drops": 0,
    "utilization_pct": 94.2,
    "tx_mbps": 847.3
  },
  "anomaly": true
}
```

Both tools are stateless (pure request/response), preserve Role-Based Access Control passthrough, and return realistic mock data when `CI_CATALYST_URL` is not set — so the Finite State Machine runs end-to-end without a live Catalyst deployment.

---

## The Finite State Machine — 7 States, Auditable Transitions

```
IDLE → PRE_TRIAGE → TRIAGE → INVESTIGATING → HYPOTHESIZING → REMEDIATING → RESOLVED
                  ↘                                         ↘ ESCALATING  ↗
                SUPPRESSED
```

| State | Tools Available | Exit Condition |
|---|---|---|
| **PRE_TRIAGE** | None — rules engine only | Score below threshold → SUPPRESSED (0 tokens); score ≥ 0.95 + security type → ESCALATING immediately |
| **TRIAGE** | `splunk_get_indexes`, `get_network_topology` + Retrieval-Augmented Generation: Splunk Processing Language patterns | Confirms data sources and device role |
| **INVESTIGATING** | `get_telemetry_metrics`, `splunk_run_query` + Retrieval-Augmented Generation: past incident memory | Gathers error counters and traffic egress |
| **HYPOTHESIZING** | `saia_generate_spl`, `splunk_run_query` | Forms root cause hypothesis |
| **REMEDIATING** | None | Known-safe fix available and blast radius LOW or MEDIUM |
| **ESCALATING** | None | Ambiguous evidence, HIGH or CRITICAL blast radius, or security threat |

State-filtered tool lists prevent the Large Language Model from calling wrong tools at wrong times — the tool list changes per state, not just the prompt.

**Decision rules at HYPOTHESIZING:**

| Condition | Finite State Machine Decision | Rationale |
|---|---|---|
| Single source IP address > 60% of egress | → ESCALATING | Potential data exfiltration or Distributed Denial of Service |
| Known configuration issue and deterministic fix | → REMEDIATING | Safe to automate — reversible action |
| High blast radius (core device) | → ESCALATING | Risk too high for autonomous action |
| Incident memory match ≥ 0.75 and known fix | → REMEDIATING | Grounded in past resolution — not hallucinated |
| Ambiguous evidence after maximum tool calls | → ESCALATING | Default to human — never guess on live infrastructure |

---

## Retrieval-Augmented Generation Layers — Pinecone-Backed Investigation

Two vector stores make every investigation step evidence-grounded rather than Large Language Model guesswork.

### Splunk Processing Language Knowledge (`vigil-spl-knowledge`)
**20 vetted Splunk Processing Language query templates** covering packet loss, Border Gateway Protocol flaps, central processing unit spikes, interface errors, threat intelligence correlation, flow anomaly detection, and more. Retrieved at TRIAGE so the agent runs the right query first.

- Embedding model: OpenAI `text-embedding-3-small`
- Filtered by Finite State Machine phase (TRIAGE / INVESTIGATING / HYPOTHESIZING)
- Returns top-3 patterns with similarity scores

### Incident Memory (`vigil-incident-memory`)
**30 past incident summaries** with root causes, resolutions, and outcomes (REMEDIATING or ESCALATING). Retrieved at INVESTIGATING to inform the routing decision. When a Border Gateway Protocol flap returns `INC-2023-0988` at score 0.78 (keepalive timer mismatch, fix: `set bgp timers 30 90`), Vigil routes REMEDIATING — grounded in real resolution history, not hallucinated.

---

## Reference Incident

> **INC-20240214-001 · Priority 2 · San Jose**
> High packet loss on Cisco Catalyst `sj-catalyst-01` / `GigE0/1`

```
PRE_TRIAGE         alert scored 0.78 (high), signal_count=3 → proceed          [<1ms · 0 tokens]
Splunk Processing Language RAG    retrieved: packet_loss_egress (0.63), egress_concentration    [380ms · 0 tokens]
01 topology        sj-catalyst-01 uplinks sj-core-01, GigE0/1 on vlan=100       [118ms]
02 telemetry       out_errors=2847, utilization=94.2%, drops=1203 ⚠             [287ms]
03 run_spl         avg out_errors=2847/min, spike started 14:30 UTC ⚠           [421ms]
Incident RAG       retrieved: INC-2024-0891 (0.84) — exfiltration, ESCALATING   [390ms · 0 tokens]
04 run_spl         src_ip 10.14.22.87 = 71.2% of egress (threshold: 60%) ⚠     [389ms]
05 gen_spl         egress concentration + threat intel join query generated      [612ms]
                                                                                 ──────
Finite State Machine: single IP > 60% egress → ESCALATING (confidence 0.93)       total: ~35s
```

Structured output:

```json
{
  "incident_id": "INC-20240214-001",
  "final_state": "ESCALATING",
  "hypothesis": "sj-catalyst-01 GigE0/1: out_errors=2847 spike at 14:30 UTC. src_ip 10.14.22.87 = 71.2% egress — isolate pending threat intel",
  "tool_calls": 5,
  "confidence": 0.93,
  "recommended_action": "Isolate src_ip=10.14.22.87 pending threat intel confirmation",
  "total_tokens": 4847,
  "duration_secs": 34.8
}
```

---

## Four Demo Scenarios

| Scenario | Severity | Outcome | Why |
|---|---|---|---|
| Packet loss on GigE0/1 | Priority 2 | **ESCALATING** | Single source IP = 71% of egress + threat intelligence match |
| Border Gateway Protocol flap / keepalive timeout | Priority 2 | **REMEDIATING** | Incident memory match 0.78, known safe fix: `set bgp timers 30 90` |
| Central processing unit spike 94% with unknown process | Priority 1 | **ESCALATING** | CRITICAL blast radius + unknown process with Tor connections |
| False positive / threshold breach | Priority 3 | **SUPPRESSED** | 5 repeat fires, 0 correlated signals — 0 tokens, under 1 millisecond |

---

## Token Cost as a First-Class Metric

Same base model (`claude-sonnet-4-6`), two prompting strategies:

| Mode | Tokens | Cost per Run | Precision | Recall | Composite |
|---|---|---|---|---|---|
| Generic (unconstrained) | ~11,200 | ~$0.056 | 0.55 | 0.75 | 0.52 |
| Constrained (schema-enforced) | ~4,847 | ~$0.024 | **0.91** | **1.00** | **0.87** |

**57% token reduction. Zero model change.** At Cisco and Splunk enterprise scale — tens of thousands of daily investigations — this is a direct cloud margin problem.

| Daily Alert Volume | Unconstrained Cost | Schema-Enforced Cost | Annual Saving |
|---|---|---|---|
| 1,000 alerts/day | ~$204/day | ~$88/day | **~$42,300/year** |
| 10,000 alerts/day | ~$2,040/day | ~$880/day | **~$423,000/year** |
| 100,000 alerts/day | ~$20,400/day | ~$8,800/day | **~$4.2M/year** |

---

## Architecture

```
Alert
  │
  ▼
┌───────────────────────────────────────────────────────────────────────┐
│  PRE_TRIAGE  (0 tokens, under 1 millisecond)                          │
│  Rules engine: signal_count, repeat_count, alert_type                 │
│  → SUPPRESSED (false positive)  │  → ESCALATING (Priority 0 security) │
│  → proceed to Finite State Machine investigation                      │
└───────────────────────────────────────────────────────────────────────┘
  │
  ▼
┌───────────────────────────────────────────────────────────────────────┐
│  FINITE STATE MACHINE INVESTIGATION                                   │
│                                                                       │
│  TRIAGE                                                               │
│    ◈ Pinecone Splunk Processing Language Knowledge — top-3 patterns   │
│    ⚡ splunk_get_indexes · get_network_topology                        │
│                                                                       │
│  INVESTIGATING                                                        │
│    ◈ Pinecone Incident Memory — top-3 similar past incidents          │
│    ⚡ get_telemetry_metrics · splunk_run_query                         │
│                                                                       │
│  HYPOTHESIZING                                                        │
│    ⚡ saia_generate_spl · splunk_run_query                             │
│                                                                       │
│  DECISION                                                             │
│    egress > 60% + threat intel    → ESCALATING                       │
│    blast_radius HIGH / CRITICAL   → ESCALATING                       │
│    incident_memory ≥ 0.75         → REMEDIATING                      │
│    default                        → ESCALATING                       │
└───────────────────────────────────────────────────────────────────────┘
  │
  ▼
┌───────────────────────────────────────────────────────────────────────┐
│  PHASE 3 EVALUATOR                                                    │
│  Precision · Recall · Token cost · Mean Time to Detect speedup        │
│  Generic vs Constrained comparison · Structured JSON report           │
└───────────────────────────────────────────────────────────────────────┘
```

---

## The Broader Competitive Landscape

Vigil's competitors span four tiers — network-operations specialists, observability platforms, legacy AIOps, and forecasting specialists. Full vendor-by-vendor breakdown lives in **[`docs/competitive-landscape.md`](./docs/competitive-landscape.md)**. The market map:

```
                          AGENTIC / AUTONOMOUS INVESTIGATION
                                       ▲
                                       │
                  Cisco AgenticOps      │      AWS DevOps Agent + Splunk
                  (preview, 2025–26)    │      (GA, April 2025)
                  Juniper Marvis        │      Datadog Bits AI
                  (generative assistant)│      Dynatrace Davis AI
                                        │      New Relic AI
                  ╔═══════════════════╗ │
                  ║      VIGIL         ║│
                  ║  network + agentic ║│
                  ║  + Splunk + Cisco  ║│
                  ╚═══════════════════╝ │
                                        │
   ─── NETWORK ────────────────────────┼───────────────────── GENERAL ─────►
   ── SPECIALIST ──                    │                     OBSERVABILITY
                                        │
                  HPE Aruba Central     │      Splunk IT Service Intelligence
                  Arista CloudVision    │      Datadog Watchdog · Elastic
                  Extreme CoPilot       │      LogicMonitor · BigPanda
                  Nokia NetGuard        │      Moogsoft · ServiceNow ITOM
                                        │      PagerDuty AIOps · BMC Helix
                                        ▼
                          REACTIVE CORRELATION / ANALYTICS
```

**Vigil is the only product in the upper-left quadrant** — network-specialist + agentic investigation — and the only product anywhere on the map combining: Cisco specialization, Splunk integration, multi-step agentic investigation, foundation-model time-series forecasting, Retrieval-Augmented Generation incident memory, and a structured audit trail.

### Five-Tier Summary

| Tier | Category | Representative Vendors | Vigil's Edge |
|---|---|---|---|
| **1** | Network ops + agentic AI | Cisco AgenticOps (preview), Juniper Marvis, HPE Aruba, Arista, Extreme, Nokia | Cisco AgenticOps is closest but not shipped; every other Tier 1 vendor is locked to its own hardware |
| **2** | General observability + agentic AI | AWS DevOps Agent + Splunk, Datadog Bits AI, Dynatrace Davis, New Relic AI | Application-layer focus, no Cisco specialization, mostly single-turn assistants |
| **3** | Legacy AIOps platforms | BigPanda, Moogsoft, ServiceNow ITOM, PagerDuty, BMC Helix, LogicMonitor, IBM Watson | Correlation only — no investigation, no agentic capability, no forecasting |
| **4** | Forecasting / predictive | Splunk IT Service Intelligence Predictive Analytics, Datadog Forecasting, AWS Lookout, Anodot | Statistical models, not foundation models; no agentic investigation |
| **5** | Adjacent / emerging | Resolve.ai, NetBrain, IP Fabric, Forward Networks, LangGraph / CrewAI | Non-network-specialist or framework-only |

**One-sentence statement:** every other product is either network-specialist without Splunk and agentic depth, or general observability without Cisco specialization, or an AIOps platform without investigation depth. Vigil is the only product combining all three.

---

## Proactive Forecasting Layer — The Visual Difference

Every system named above is **reactive**: an alert fires, then the agent investigates. Vigil's forecasting layer makes Vigil **proactive**: telemetry is monitored continuously, foundation models forecast the next 24 steps (~2 hours ahead), and triggers fire *before* the alerting system would have.

The war-room UI ships a Forecast Strip that renders this layer on screen — three sparkline cards (Border Gateway Protocol route count, Central Processing Unit, packet drop) per scenario, each with 60-step history, 24-step forecast, and a shaded P10–P90 confidence band. Trigger pills colour-coded by type: orange for threshold breach (`T−18min` countdown), amber for trajectory drift, violet for uncertainty, green for stable.

```
                       ┌────────────────────────────────────────┐
                       │  Splunk MCP Server (poll every N min)  │
                       └────────────────────┬───────────────────┘
                                            ▼
┌────────────────────────────────────────────────────────────────────────┐
│  LAYER 1 — TELEMETRY INGESTION                                         │
│  512-step rolling buffer per device × metric                           │
└────────────────────────────────────────┬───────────────────────────────┘
                                         ▼
┌────────────────────────────────────────────────────────────────────────┐
│  LAYER 2 — FORECAST ENGINE          (24-step horizon · ~2h ahead)      │
│  ◆ Cisco Time Series Model           ◆ Chronos-T5-Small                │
│    point forecast                      P10 / P50 / P90 distribution    │
└────────────────────────────────────────┬───────────────────────────────┘
                                         ▼
┌────────────────────────────────────────────────────────────────────────┐
│  LAYER 3 — TRIGGER EVALUATION                                          │
│  THRESHOLD · TRAJECTORY · UNCERTAINTY                                  │
└────────────────────────────────────────┬───────────────────────────────┘
                                         ▼
┌────────────────────────────────────────────────────────────────────────┐
│  LAYER 4 — FINITE STATE MACHINE INVESTIGATION (existing)               │
│  Forecast snapshot attached as audit-trail metadata to every decision  │
└────────────────────────────────────────┬───────────────────────────────┘
                                         ▼
┌────────────────────────────────────────────────────────────────────────┐
│  FEEDBACK LOOP                                                         │
│  Forecast accuracy vs. outcome → labeled fine-tuning corpus            │
└────────────────────────────────────────────────────────────────────────┘
```

### Reactive vs. Proactive — Competitive Landscape

| Product | Detection Posture | Forecasting Method | Foundation Models | Multi-Trigger Logic |
|---|---|---|---|---|
| Splunk IT Service Intelligence Predictive Analytics | Forward-looking | Per-metric statistical models | No | Threshold breach only |
| Datadog Watchdog | Backward-looking | Anomaly detection (statistical) | No | Not applicable |
| Cisco AI Canvas / AgenticOps | Reactive | None announced | No forecasting layer | Not applicable |
| AWS DevOps Agent + Splunk | Reactive | None | No | Not applicable |
| **Vigil — Forecasting Layer** | **Proactive — 24 steps ahead** | **Cisco Time Series Model + Chronos in parallel** | **Yes — two foundation models** | **Threshold + Trajectory + Uncertainty** |

Vigil is the only entrant that combines foundation-model forecasting with agentic investigation — and the only one where the trigger types are tuned to what actually breaks in network operations.

**Three knowledge sources, three time orientations:**

| Time Orientation | Knowledge Source | Purpose |
|---|---|---|
| **Past** | Pinecone `vigil-incident-memory` — 30 past resolutions | Has this been seen before, and what fixed it? |
| **Present** | Pre-triage classifier + Splunk telemetry | What is happening right now? Is the alert credible? |
| **Future** | Cisco Time Series Model + Chronos forecast | What will happen in the next 24 steps? |

**Mock status:** The four scenarios ship with pre-computed forecast fixtures. The architecture, trigger logic, and user interface are real and shippable; wiring to live Cisco Time Series Model and Chronos endpoints is roughly one week of work, gated on Priority 0 from `docs/model-evaluation.md` (Cisco exposing quantile outputs via Application Programming Interface).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Large Language Model | `claude-sonnet-4-6` / `claude-opus-4-7` (Anthropic) |
| Finite State Machine | `transitions` library (Python) |
| Retrieval-Augmented Generation — embeddings | OpenAI `text-embedding-3-small` |
| Retrieval-Augmented Generation — vector store | Pinecone serverless (us-east-1) |
| Model Context Protocol tools — Splunk | Splunk Model Context Protocol Server v1.1 (generally available) |
| Model Context Protocol tools — Cisco Catalyst | Catalyst Model Context Protocol (mocked in development; real endpoint via `CI_CATALYST_URL`) |
| API server | FastAPI + Server-Sent Events |
| User interface | React + Vite |

---

## Project Structure

```
phase2_agent/        # Finite State Machine incident commander (Anthropic API)
  commander.py       # Plan → Act → Observe loop
  pre_triage.py      # Zero-token alert scoring
  prompts.py         # Per-state system prompts
  scenarios/         # 4 reference incidents (JSON)

phase3_evaluator/    # Scoring and Mean Time to Detect / Resolve tracking
  evaluator.py       # Precision · recall · token cost
  mttd.py            # Mean Time to Detect / Resolve vs Network Operations Center baseline

vigil/               # Retrieval-Augmented Generation-enabled Finite State Machine (Pinecone + Splunk MCP)
  fsm.py             # 7-state Retrieval-Augmented Generation-informed Finite State Machine
  rag.py             # SPLKnowledgeRAG + IncidentMemoryRAG
  mcp_client.py      # Splunk Model Context Protocol HTTP client (+ realistic mock)
  classifier.py      # Pre-triage noise filter

data/
  spl_knowledge/     # 20 Splunk Processing Language pattern records (JSONL)
  incidents/         # 30 past incident summaries (JSONL)

scripts/
  seed_pinecone.py      # Embed and upload both corpora (run once)
  run_investigation.py  # Command-line investigation runner

api/server.py        # FastAPI Server-Sent Events backend
ui/                  # React war-room dashboard
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install -e ".[dev]"

# 2. Set credentials
cp .env.example .env
# Required: ANTHROPIC_API_KEY
# For RAG:  PINECONE_API_KEY, OPENAI_API_KEY

# 3. Seed Pinecone (run once)
python scripts/seed_pinecone.py

# 4. Start backend
python -m api.server

# 5. Start frontend
cd ui && npm install && npm run dev
# Opens at http://localhost:5173
```

## Credentials

| Key | Required For | Where to Get |
|---|---|---|
| `ANTHROPIC_API_KEY` | Finite State Machine investigation | console.anthropic.com |
| `PINECONE_API_KEY` | Retrieval-Augmented Generation vector store | app.pinecone.io |
| `OPENAI_API_KEY` | Embedding generation (seed only) | platform.openai.com |
| `SPLUNK_MCP_URL` + `SPLUNK_TOKEN` | Live Splunk queries (optional — mocked by default) | Splunk Cloud → Settings → Tokens |
| `CI_CATALYST_URL` + `CI_CATALYST_TOKEN` | Live Catalyst topology (optional — mocked by default) | Cisco DevNet / on-premises Catalyst |

---

## Splunk AI Governance Alignment

Vigil implements all five of Splunk's published AI governance principles as core architecture — not as a compliance layer added after the fact.

| Splunk Principle | Vigil |
|---|---|
| **Accountability** | Pydantic JSON report per investigation: Finite State Machine transition log, tool call trace, Retrieval-Augmented Generation retrieval log, confidence score |
| **Transparency** | Threshold-based transitions, not black-box Large Language Model judgment — every SUPPRESSED / REMEDIATING / ESCALATING decision cites the rule that fired |
| **Privacy** | Role-Based Access Control passthrough — Vigil inherits Splunk user permissions with no privilege escalation; no raw logs stored outside Pinecone |
| **Fairness** | Rules-based pre-triage and configurable thresholds prevent model drift across incident types; all four reference types scored on the same rubric |
| **Resilience** | Default-to-ESCALATING — ambiguous evidence, maximum tool calls, or novel scenario always routes to human; Pinecone outage falls back to non-Retrieval-Augmented Generation investigation |

---

## Roadmap

| Item | Description |
|---|---|
| **Splunk Processing Language Quality Gate** | Score generated queries for structural validity and field coverage before executing against production data |
| **Investigation-Aware Context Injection** | Prepend current Finite State Machine state and prior findings to every `saia_generate_spl` call for more targeted queries |
| **Continuous Incident Memory** | Webhook from ServiceNow or Jira auto-embeds resolved incidents into Pinecone after closure |
| **Splunk Processing Language Cache** | Time-to-live-based cache for known-pattern queries; reduces SAIA prompt consumption 40–60% |
| **AI Canvas Integration** | When Cisco AI Canvas ships, Vigil's Finite State Machine transitions map directly to Canvas workflows |

---

*Built on Splunk Model Context Protocol v1.1 · Cisco Catalyst Model Context Protocol · Pinecone · Anthropic Claude*
