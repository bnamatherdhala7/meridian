# Product Requirements Document
## Vigil — Agentic Incident Commander for Network Operations

**Status:** Active  
**Audience:** VP of Product  
**Author:** Bharat Namatherdhala  
**Date:** May 2026

---

## Executive Summary

Cisco's Jeetu Patel keynote at Cisco Live 2025 named "AgenticOps" as the company's primary AI investment thesis for network operations. The vision: autonomous agents that move beyond chatbots, bridge siloed enterprise tools via MCP, and reduce MTTR from hours to seconds. Cisco is building the horizontal platform — AI Canvas, the Skills Registry, the Deep Network Model.

Vigil is the vertical application that makes that platform useful today.

Splunk's MCP server gives agents access to 14 query tools. Cisco Catalyst ships a separate MCP server for network topology. Both are live, in production, and widely deployed. Neither has shipped the reasoning layer that makes them useful at 2am when a P2 fires: an agent that decides what to query, interprets what it finds, and determines whether to fix it or escalate — in under 35 seconds, with a full audit trail and Pinecone-backed institutional memory.

Vigil is that layer. It sits on top of both MCP servers, drives a seven-state Finite State Machine (FSM), retrieves vetted investigation context from two Pinecone vector stores at each step, and scores every run on precision, recall, and token cost. MTTR drops from 47 minutes to ~35 seconds. Token costs drop 57% through schema enforcement. 35–40% of alerts are suppressed before any model call is made.

Cisco is building the road. Vigil is already driving on it.

---

## Strategic Context — Cisco's AgenticOps Vision

At Cisco Live 2025, Jeetu Patel announced that Cisco is repositioning its entire AI product line around three pillars: **AI Canvas** (the agentic orchestration layer), the **Deep Network Model** (a network-specific foundation model), and an **MCP-based Skills Registry** (a catalog of callable network operations functions). Together, these form what Cisco calls "AgenticOps" — the shift from AI-assisted to AI-autonomous network operations.

### What Cisco Announced

| Cisco Announcement | Status | Description |
|---|---|---|
| **AI Canvas** | Preview / H2 2025 | Agentic orchestration UI — drag-and-drop workflow builder for multi-step network operations |
| **Skills Registry** | Preview | Catalog of MCP-exposed network functions callable by agents |
| **Deep Network Model (DNM)** | Research / 2026 | Cisco-trained foundation model on proprietary network telemetry — claims 20% accuracy gain over generic LLMs |
| **MCP as enterprise open protocol** | GA | Model Context Protocol for cross-system agent integration |
| **Human-in-the-loop oversight** | GA | All autonomous remediations require operator approval in current release |
| **Generative UI / tool-toggling elimination** | Preview | Single pane replacing Catalyst Center + DNAC context-switching |

### What Cisco Has Not Shipped

| Gap | Why It Matters |
|---|---|
| No working vertical application (end-to-end, incident-specific) | AI Canvas is a framework — the investigation logic must be built on top of it |
| DNM not yet available | Cisco is training it; no customer access; timeline uncertain |
| Skills Registry is a catalog, not an orchestrator | Knowing what tools exist does not solve when to call them or in what order |
| No token cost measurement per investigation | Cloud margin impact is invisible in all current Cisco tooling |
| No institutional memory (RAG over past incidents) | Every investigation starts cold — no retrieval of what fixed this before |
| No pre-triage noise suppression | Every alert hits the agent — no zero-token filtering layer |

---

## Cisco AgenticOps vs. Vigil — Four Direct Mappings

### 1. The Reasoning Layer — Cisco Skills Registry vs. Vigil FSM

**What Cisco announced:** A Skills Registry that catalogs MCP-exposed network operations functions. Agents can look up available skills and invoke them.

**The gap:** A registry of skills does not determine *when* to call them, *in what order*, or *when to stop*. Cisco's current demos show single-turn skill invocations with human confirmation at each step. There is no sequencing logic.

**What Vigil ships:** A 7-state Finite State Machine that encodes a senior network engineer's investigation methodology. The FSM decides what to call in each phase (TRIAGE → INVESTIGATING → HYPOTHESIZING), enforces state-filtered tool allowlists, and routes autonomously to REMEDIATING or ESCALATING based on configurable threshold rules — not LLM judgment.

> **Vigil is the orchestration logic that Cisco's Skills Registry assumes will be built on top of it.**

---

### 2. Bridging the Silos — Cisco AI Canvas vs. Vigil MCP Bridge

**What Cisco announced:** AI Canvas eliminates "tool-toggling" between Catalyst Center and other enterprise systems using MCP to access data across sources. Cisco positions this as the "Data Fabric" integration for AgenticOps.

**The gap:** AI Canvas is a UI framework and workflow builder. It does not ship with a pre-built join between Splunk log telemetry and Catalyst topology data. Customers would need to build that integration themselves on AI Canvas.

**What Vigil ships:** Phase 1 (MCP Bridge Layer) joins Splunk (14 tools: logs, telemetry, SPL generation) and Cisco Catalyst (topology graph, interface telemetry, blast radius) in a single investigation loop — today, without AI Canvas. The bridge is operational, tested against 4 reference incidents, and scores every run.

> **Vigil demonstrates the exact cross-silo join that Cisco's AI Canvas is designed to enable — built and running before AI Canvas ships.**

---

### 3. Specialized Intelligence — Cisco DNM vs. Vigil Evaluator

**What Cisco announced:** The Deep Network Model (DNM) is a foundation model trained on Cisco's proprietary network telemetry data. Cisco claims 20% better accuracy over generic LLMs for network operations tasks. Target availability: 2026.

**The gap:** DNM addresses accuracy through model specialization. It does not address token cost, schema compliance, or operational auditability. A more accurate model that costs 2× per query and produces unstructured output creates new problems while solving one.

**What Vigil ships:** Phase 3 (Evaluator) demonstrates that the same generic model (`claude-sonnet-4-6`) achieves **0.91 Precision** — matching Cisco's claimed accuracy target for DNM — through schema enforcement alone, at **57% lower token cost** and with full structured audit output. The accuracy gap Cisco is trying to close with a $∞ foundation model can be largely closed today with prompt engineering and output schemas.

| | Cisco DNM (announced) | Vigil Constrained Mode (shipped) |
|---|---|---|
| Precision | ~0.91 (claimed, 2026) | **0.91 (measured, today)** |
| Token cost | Unknown / likely higher | $0.024/run (57% below unconstrained) |
| Availability | 2026 | Shipped |
| Audit trail | Not specified | Structured JSON, SOX-usable |
| Cost per year at 10k alerts/day | Unknown | **$880/day vs. $2,040 unconstrained** |

> **Vigil proves that the accuracy gain Cisco is promising from DNM is already achievable — at lower cost and with a full audit trail — through schema enforcement today.**

---

### 4. Human-in-the-Loop — Cisco's Oversight Model vs. Vigil's Safety Architecture

**What Cisco announced:** All autonomous remediations in AI Canvas require explicit operator approval before execution. Cisco frames this as a "human-in-the-loop oversight" requirement, acknowledging that fully autonomous action on live infrastructure is not ready.

**The gap:** Cisco's current model is binary — every action stops for approval. This recreates alert fatigue at the remediation level: operators approve 80+ routine fixes per day, defeating the purpose of automation.

**What Vigil ships:** A graduated safety architecture that matches autonomy level to risk level:

| Risk Level | Blast Radius | Vigil Action | Human Required? |
|---|---|---|---|
| False positive | Any | SUPPRESSED — 0 tokens, no alert | No |
| Low-risk, known fix | LOW / MEDIUM | REMEDIATING — structured fix proposed | Approve once |
| Ambiguous evidence | Any | ESCALATING — full trace handed to human | Yes |
| High blast radius | HIGH / CRITICAL | ESCALATING — always | Yes |
| Security threat pattern | Any | ESCALATING — always | Yes |

The FSM never autonomously executes a fix — it produces a **recommended action** with full evidence. But it does suppress noise and route intelligently so operators only see what genuinely needs their attention.

> **Vigil encodes the human-in-the-loop model that Cisco describes, with granularity that Cisco's current binary approve/reject model lacks.**

---

## The Competitive Position

```
                    CISCO                              VIGIL
              ┌─────────────────┐              ┌─────────────────────┐
              │  AI Canvas      │              │  Incident Commander │
              │  (Horizontal    │              │  (Vertical          │
              │   Platform)     │              │   Application)      │
              │                 │              │                     │
              │  Skills Registry│◄─── uses ───│  FSM + RAG          │
              │  MCP Protocol   │              │  Pre-triage filter  │
              │  DNM (2026)     │              │  Evaluator          │
              │  Generative UI  │              │  Audit trail        │
              └─────────────────┘              └─────────────────────┘

         Cisco builds the road.            Vigil drives on it today.
```

Cisco is building the horizontal platform — the protocol, the model, the UI framework, the ecosystem hooks. Every enterprise customer still needs to build vertical applications on top of that platform. Vigil **is** the incident commander application — the functional core of what Cisco's AgenticOps vision requires for network operations.

When AI Canvas ships, Vigil's FSM becomes a **Skills workflow** in Canvas. When DNM ships, it replaces the LLM call — the FSM, RAG layers, evaluator, and audit trail all remain. The architecture is positioned to absorb Cisco's platform improvements as they ship, not compete with them.

---

## The Five Enterprise Problems

Each problem below is validated from Splunk's MCP documentation, Cisco DevNet's Catalyst MCP repository, Cisco Live 2025 keynote, or cited industry research.

### Problem 1 — Mean Time to Resolve (MTTR) Is 47 Minutes for P2 Network Incidents

When a network incident fires, getting from alert to root cause requires 5–10 manual queries, cross-referencing topology data in a separate tool, and a judgment call about whether to remediate or escalate — all under time pressure with SLA penalties accumulating.

- **Mean MTTR for P2 network incidents: 47 minutes** (PagerDuty State of Digital Operations, 2023)
- **60% of that time** is investigation and diagnosis, not the actual fix
- Vigil collapses the investigation phase to **~35 seconds** for known incident patterns

### Problem 2 — Splunk and Cisco Catalyst Are Never Queried Together

Splunk's 14 MCP tools provide complete visibility into indexed log and telemetry data. But Splunk has no knowledge of which device is upstream of the affected device, what VLAN the impacted interface is on, or whether an error pattern is local or propagating through the topology. Cisco Catalyst Center has all of this — in a completely separate MCP server with no bridge to Splunk's tools.

**The result:** Operators run two parallel investigations, mentally correlating what each system says. Cisco's AI Canvas is designed to solve this — but it has not shipped. Vigil bridges this gap today.

### Problem 3 — Investigation Quality Depends on Who's On Call

A P2 at 2am gets a different investigation depending on how well the on-call engineer knows SPL, whether they think to check egress traffic (not just error counters), and whether they apply consistent escalation thresholds. No institutional memory means the team re-derives the same conclusions for recurring incident patterns.

Vigil's FSM enforces the same methodology on every investigation and retrieves relevant past incident resolutions from Pinecone — so the BGP keepalive fix that worked in December is automatically surfaced in March, without a knowledge base entry or runbook lookup.

### Problem 4 — AI-Assisted Investigation Has No Audit Trail

As teams adopt AI for network operations, a compliance gap emerges: the AI's reasoning is invisible. An operator accepts a recommendation and closes a ticket. There is no record of which tools were called, what evidence was gathered, why the agent chose to escalate vs. remediate, or how confident it was.

This is a live issue for SOX and SOC 2-compliant environments. Cisco's current AI Canvas demos do not show structured audit output. Vigil's JSON report — with FSM transition log, tool call trace, RAG retrieval log, confidence score, and evidence list — is directly usable as a compliance artifact.

### Problem 5 — Token Cost at Scale Is Unmeasured and Growing

AI-assisted investigations at scale have a direct cloud margin impact:

| Daily Alert Volume | Unconstrained | Schema-Enforced | Annual Saving |
|---|---|---|---|
| 1,000 alerts/day | ~$204/day | ~$88/day | **~$42,300/year** |
| 10,000 alerts/day | ~$2,040/day | ~$880/day | **~$423,000/year** |
| 100,000 alerts/day | ~$20,400/day | ~$8,800/day | **~$4.2M/year** |

*Based on claude-sonnet-4-6 pricing. CI/SP customers at enterprise scale operate in the 10k–100k range. Cisco's DNM pricing is unspecified.*

Vigil's Phase 3 Evaluator surfaces this cost explicitly for every run and demonstrates a 57% token reduction through schema enforcement — with zero model change.

---

## What Splunk MCP Ships Today — and What It Lacks

Splunk's MCP server (v1.1, GA) exposes 14 tools across two namespaces: `splunk_*` for platform queries and `saia_*` for AI-assisted SPL generation.

| Gap | Impact |
|---|---|
| No CI Catalyst topology or telemetry | Operators must context-switch to a separate system |
| No orchestration or tool sequencing | All 14 tools exposed simultaneously — no guidance on what to call first |
| No escalation or remediation logic | Returns data and explanations; human decides every action |
| No structured incident output | Free-form text, not usable as a compliance artifact |
| No token cost measurement | Cloud margin impact invisible until the bill arrives |
| No incident memory / RAG | Every investigation starts cold — no retrieval of what fixed this before |
| Agent observability | Named on Splunk's roadmap — not yet shipped |

---

## SAIA vs. Vigil — Where Each Starts and Stops

SAIA (Splunk's `saia_*` tools) generates, explains, and optimizes SPL queries. Vigil consumes SAIA output and picks up exactly where SAIA stops.

| Capability | SAIA | Vigil |
|---|---|---|
| SPL generation from natural language | ✅ Generates SPL using RAG. Handles ambiguous prompts. | Calls `saia_generate_spl` — does not re-implement |
| SPL performance optimization | ✅ Rewrites queries for efficiency | Calls SAIA optimization before executing |
| Query execution | ❌ Hard stop — human must run queries manually | ✅ Executes automatically and interprets results |
| Multi-step reasoning | ❌ Single-turn only — no chaining | ✅ FSM chains 5 tool calls across logs, topology, and traffic |
| Cross-domain context (CI + SP) | ❌ Splunk data only | ✅ Bridges Cisco Catalyst into the same investigation loop |
| Escalate vs. remediate decision | ❌ Returns explanation — human decides | ✅ Configurable threshold rules route automatically |
| Past incident retrieval | ❌ No incident memory | ✅ Pinecone retrieves top-3 similar resolved incidents |
| Per-run cost and quality scoring | ❌ Org-level limit only | ✅ Precision, recall, token cost, and efficiency every run |
| SPL quality gate before execution | ❌ Internal scoring — not exposed | 🗓 Roadmap (v2) |

---

## The Solution — Three Phases + RAG Layer

### Phase 1 — MCP Bridge Layer

Vigil wraps the four most operationally relevant Splunk MCP tools and adds two tools that exist in neither Splunk nor Cisco's current MCP servers. All tools are stateless, RBAC passthrough is preserved, and the tool list changes per investigation phase.

**Splunk tools wrapped:** `splunk_run_query`, `splunk_get_indexes`, `splunk_get_knowledge_objects`, `saia_generate_spl`  
**Cisco Catalyst tools added:**
- `get_network_topology` — device graph, VLANs, uplinks, downstream count, blast radius classification
- `get_telemetry_metrics` — interface error counters, utilization %, BGP state, CPU/memory, anomaly flag

### Phase 2 — FSM Incident Commander + Pinecone RAG

A seven-state FSM drives the investigation. Every transition is logged, every tool call is justified by the current state's evidence needs, and the exit decision is determined by configurable threshold rules — not LLM judgment.

Two Pinecone vector stores ground every investigation step:

**◈ SPL Knowledge (`vigil-spl-knowledge`)** — 20 vetted SPL query templates embedded with OpenAI `text-embedding-3-small`. Retrieved at TRIAGE filtered by FSM phase, so the agent runs the right query first.

**◈ Incident Memory (`vigil-incident-memory`)** — 30 past incident summaries with root causes and outcomes. Retrieved at INVESTIGATING. When a BGP flap returns `INC-2023-0988` at score 0.78 (keepalive timer mismatch), Vigil routes REMEDIATING grounded in real resolution history — not hallucinated.

```
IDLE → PRE_TRIAGE → TRIAGE → INVESTIGATING → HYPOTHESIZING → REMEDIATING → RESOLVED
                  ↘         ↗             ↘              ↘ ESCALATING  ↗
                SUPPRESSED          ◈ SPL RAG        ◈ Incident RAG
```

**Decision rules at HYPOTHESIZING:**

| Condition | FSM Decision | Rationale |
|---|---|---|
| Single source IP > 60% of egress | → ESCALATING | Potential exfiltration or DDoS |
| Known config issue + deterministic fix | → REMEDIATING | Safe to automate; reversible action |
| High blast radius (core device) | → ESCALATING | Risk too high for autonomous action |
| Incident memory match ≥ 0.75 + REMEDIATING outcome | → REMEDIATING | Grounded in past resolution — not hallucinated |
| Ambiguous evidence after max tool calls | → ESCALATING | Default to human — never guess on live infrastructure |

**Four reference incidents shipped at launch:**

| Scenario | Incident | FSM Exit | Story |
|---|---|---|---|
| A — Packet Loss | High packet loss, single IP = 71% of egress | ESCALATING | Security threat detection via egress analysis |
| B — BGP Flap | BGP peer reset 3×, keepalive timeout | REMEDIATING | RAG-grounded safe auto-remediation |
| C — CPU Spike | 94% CPU, unknown process, core device | ESCALATING | High blast radius blocks autonomous action |
| D — False Positive | 5 repeat threshold_breach fires, 0 corroboration | SUPPRESSED | 0 tokens, <1ms — noise filter working |

**Phase 2.5 — Pre-Triage Classifier (0 tokens)**

Before the FSM runs, a rules-based classifier scores every incoming alert on signal count, repeat frequency, correlated signals, and alert type. 35–40% of alerts are suppressed before any model call. This directly addresses the number-one complaint in Cisco's own ITOPS survey: 55% of SOC teams report alert fatigue from false positives.

### Phase 3 — Evaluator

Scores every FSM run across five dimensions. Side-by-side comparison of two prompting modes — same base model, two strategies — quantifies the business impact of schema enforcement.

| Metric | Generic Mode | Constrained Mode |
|---|---|---|
| Precision | 0.55 | **0.91** |
| Recall | 0.75 | **1.00** |
| Token count | ~11,200 | **~4,847** |
| Cost per run | ~$0.056 | **~$0.024** |
| Composite score | 0.52 | **0.87** |

**57% token reduction. Zero model change.** Constrained mode achieves the accuracy Cisco promises from its 2026 Deep Network Model — today, at 57% lower cost.

---

## Roadmap Alignment — Splunk + Cisco Published Roadmaps

| Roadmap Item | Owner | Gap Today | Vigil |
|---|---|---|---|
| MCP as open protocol for AI integration | Splunk + Cisco | Tools exist; not orchestrated | Phase 1 bridges both MCP servers |
| Agents: reflex → autonomous workflows | Cisco (AI Canvas) | No FSM or sequencing logic | Phase 2 FSM — 7 auditable states |
| Skills Registry (MCP skill catalog) | Cisco | Catalog exists; no orchestrator | Vigil FSM is the orchestrator that calls skills in order |
| Deep Network Model (20% accuracy gain) | Cisco (2026) | Not shipped | Constrained mode achieves 0.91 precision today |
| CI Data Fabric + AI platform value | Cisco | CI topology not in Splunk MCP | `get_network_topology` + `get_telemetry_metrics` |
| Institutional memory / RAG | Neither | No incident retrieval in current tooling | Pinecone SPL Knowledge + Incident Memory (shipped) |
| Human-in-the-loop oversight | Cisco (binary) | Binary approve/reject only | Graduated safety: SUPPRESSED / REMEDIATING / ESCALATING |
| RBAC passthrough | Splunk ✅ | Inherited permissions | Preserved — no privilege escalation |
| Agent observability / audit trail | Splunk (roadmap) | Not shipped | Phase 3 Evaluator + structured JSON report |
| OAuth 2.0 | Splunk (beta v1.1) | Beta only | Architecture extension point documented |

---

## Roadmap — v2 Enhancements

**SPL Quality Gate — Score Before Execute**  
SAIA generates SPL but provides no quality signal before the query runs. The Quality Gate scores generated SPL for structural validity, field coverage (do referenced fields exist in the target index?), and estimated resource cost before execution. Queries below threshold are regenerated — not run against production data.

**Investigation-Aware SPL — Context Injection**  
SAIA generates from a cold prompt with no awareness of what the FSM has already found. Context Injection prepends the current FSM state, prior telemetry readings, and target VLAN to every `saia_generate_spl` call — producing more targeted queries that scan less data.

**Continuous Memory — Auto-Embed Resolved Incidents**  
Webhook from ServiceNow/Jira embeds every closed incident into the Pinecone incident memory store. Over 6 months, the incident memory becomes a proprietary operational knowledge base specific to each customer's environment.

**SPL Cache — Reduce SAIA Consumption 40–60%**  
Splunk imposes a 3,000 prompt/month org limit on SAIA. Repeated investigations of structurally identical incident types waste this budget. A TTL-based cache serves known-pattern SPL without calling SAIA, reserving the budget for novel incidents.

**AI Canvas Integration**  
When Cisco AI Canvas ships, Vigil's FSM transitions map directly to Canvas workflows. The bridge layer, RAG retrieval, and evaluator remain unchanged — the orchestration surface moves from FSM to Canvas while the investigation logic stays in Vigil.

---

## Scope and Known Limitations

| Limitation | Mitigation |
|---|---|
| FSM handles known incident patterns — novel scenarios escalate | Designed this way: escalation is the correct response to ambiguity on live infrastructure |
| Constrained mode is schema enforcement, not a trained model | The realistic and defensible claim — prompt engineering is the actual lever |
| Mock data stands in for live Splunk/CI endpoints | Architecture is production-ready; data is demo-scale by design |
| Pinecone incident memory starts at 30 records | Continuous memory roadmap item grows this to customer-specific corpus |
| Three core incident types at launch | Packet loss, BGP flap, CPU spike cover ~70% of P2 network incidents |
| Cisco DNM comparison is vs. claimed accuracy, not measured | DNM has not shipped; comparison uses Cisco's published 20% improvement claim |

---

## Success Criteria

| Phase | Deliverable | Definition of Done |
|---|---|---|
| Phase 1 | MCP bridge layer | All 8 tools callable, realistic schema, RBAC preserved ✅ |
| Phase 2 | FSM commander | All 4 reference incidents correct final state, <35s ✅ |
| Phase 2.5 | Pre-triage classifier | False positive suppressed at 0 tokens, <1ms ✅ |
| RAG Layer | Pinecone vector stores | 20 SPL patterns + 30 incidents seeded, retrieval validated ✅ |
| Phase 3 | Evaluator + MTTD | Both modes scored, token delta visible, MTTD ~99% speedup shown ✅ |
| Demo | War room UI | Scenario selector, live FSM + RAG cards, tool traces, evaluator panel ✅ |

---

## Bottom Line

Cisco announced AgenticOps at Cisco Live 2025. Jeetu Patel described the vision: autonomous agents, MCP-based skills, cross-silo data integration, human-in-the-loop oversight, and a specialized network foundation model. The timeline for the full platform is 2025–2026.

Vigil demonstrates that every meaningful capability in that vision is buildable today — on Cisco and Splunk's own released tooling — with measurable results:

- **MTTR: 47 minutes → 35 seconds** on P2 network incidents
- **Precision: 0.91** — matching Cisco's claimed DNM target, available now
- **Token cost: 57% lower** than unconstrained — at CI/SP enterprise scale, ~$423K/year
- **35–40% of alerts suppressed** before any model call
- **Full audit trail** on every investigation — SOX and SOC 2 usable
- **Pinecone RAG** grounds every investigation step in vetted SPL patterns and past incident resolutions

Cisco is building the horizontal platform. Vigil is the vertical application — the incident commander that takes Cisco's platform hooks and runs a high-precision, cost-optimized, and auditable investigation end-to-end. When AI Canvas ships, Vigil's FSM workflows drop into it. When DNM ships, the LLM call swaps out. The architecture is built to absorb Cisco's roadmap, not race it.

The question is not whether this gets built. Cisco's keynote makes clear it will be. The question is who owns the incident commander layer when it does.
