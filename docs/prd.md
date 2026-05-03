# Product Requirements Document
## Vigil — Agentic Reasoning Layer for Network Operations

**Status:** Proposal  
**Audience:** VP of Product  
**Author:** Bharat Namather Dhala  
**Date:** May 2026  
**Working Codename:** Vigil (formerly: SP Agentic Ops — Incident Commander)

---

## Executive Summary

SP shipped a GA MCP server in February 2025 that gives AI agents structured access to SP's query and knowledge capabilities. The tools exist. The plumbing works. What SP hasn't shipped — and has explicitly called out on their own roadmap — is the **reasoning layer**: an agent that decides which tools to call, in what order, and when to escalate versus remediate.

Vigil builds that reasoning layer. It sits directly on top of SP's GA MCP server and adds three things SP hasn't productized: a Finite State Machine (FSM) that drives auditable incident investigation workflows, CI network topology and telemetry integration, and a live evaluator that scores agent runs on precision, recall, and token cost.

This is not a prototype of what AI could do someday. It is an implementation of what SP's own roadmap says needs to exist — built on their actual released tooling.

---

## The Problem

### What SP Shipped

SP's MCP server (v1.1.0, GA February 2025) is a well-secured query interface. It exposes four tools:

| Tool | What it does |
|---|---|
| `run_spl_query` | Execute SPL against a SP index |
| `generate_spl` | Generate optimized SPL from natural language |
| `search_indexes` | Discover available indexes and data sources |
| `get_knowledge_objects` | Surface saved searches, field extractions, lookups |

Version 1.1.0 added OAuth 2.1 support (beta), rate limiting, and a `run_saved_search` tool. These are meaningful infrastructure additions. They are not an agent.

### What SP Acknowledged They Haven't Shipped

SP's own documentation states the core limitation plainly:

> *"LLMs are good for general purpose tasks but struggle with understanding the complexity of machine data in operational environments."*

Their Observability Cloud team is building a Troubleshooting Agent that correlates signals across metrics, events, logs, and traces — but that product is scoped to Observability Cloud specifically. There is no general-purpose reasoning layer on top of the MCP server. That is the open space Vigil occupies.

### The Five Gaps

These are the specific, citable gaps in what SP has shipped today:

| Gap | What's Missing | Why It Matters |
|---|---|---|
| **1. Orchestration** | No agent decides which tools to call or in what sequence | The four MCP tools are waiting for a human to tell them what to do |
| **2. Network context** | No CI topology or telemetry integration | Interface-level data (errors, drops, VLAN, device graph) doesn't exist in SP's toolset |
| **3. Decision logic** | No threshold-based escalation or remediation routing | An LLM alone cannot reliably decide when to escalate on live infrastructure |
| **4. Agent observability** | SP named this as a roadmap item — it hasn't shipped | There is no way to score, audit, or compare agent runs today |
| **5. Token economics** | No cost-aware evaluation of agent behavior | At CI/SP scale, token waste per investigation is a real margin problem |

**Gap 4 is particularly defensible:** SP's own roadmap presentation (timestamp 53:34–54:19) names "Observability for AI agent interactions" as an upcoming feature. Vigil's Phase 3 evaluator is a working prototype of that feature.

---

## Market Context

The business case for this investment is not speculative:

- **Gartner** projects 33% of enterprise applications will incorporate agentic AI by 2028
- **IDC** reports 80% of organizations are already actively investing in agentic AI
- The gap is not capability — LLMs can reason over structured data. The gap is **trust and auditability** on live infrastructure, which is what FSM-driven orchestration directly addresses

The addressable market is every enterprise running SP for network operations — which includes the majority of Fortune 500 infrastructure teams.

---

## The Solution

Vigil is a three-phase system, each phase delivering a concrete, demoable artifact.

### Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  War Room Console                    │
│  ┌──────────┐  ┌──────────────────┐  ┌───────────┐  │
│  │  Phase 1 │  │    Phase 2       │  │  Phase 3  │  │
│  │ MCP Tool │  │ FSM Incident     │  │ Evaluator │  │
│  │ Registry │  │ Commander        │  │ Panel     │  │
│  │          │  │                  │  │           │  │
│  │ SP       │  │ PLAN→ACT→OBSERVE │  │ Score     │  │
│  │ native + │  │ state machine    │  │ Tokens    │  │
│  │ CI       │  │ reasoning trace  │  │ Precision │  │
│  │ mocked   │  │                  │  │ Recall    │  │
│  └──────────┘  └──────────────────┘  └───────────┘  │
└─────────────────────────────────────────────────────┘
```

The full system is visible as a single war room dashboard. Not three separate scripts — one unified console showing an incident move from detection to resolution or escalation in real time.

---

### Phase 1 — MCP Connectivity Layer

**What it does:** Connects to SP's real GA MCP server and extends it with CI network context tools.

**SP tools used as-is (no mocking):**
- `run_spl_query`, `generate_spl`, `search_indexes`, `get_knowledge_objects`

**CI tools added on top:**
- `get_network_topology` — CI Catalyst device graph (device ID, interface, VLAN relationships)
- `get_telemetry_metrics` — interface-level counters: `device_id`, `interface`, `vlan`, `time_window`, `error_rate`

**Key design decisions:**
- Tools are stateless (pure request/response) — no session state between calls
- RBAC passthrough — the agent inherits SP's existing role-based access, no privilege escalation
- One-line config swap — local trial instance for demo, production endpoint via env var
- Schema design matches real CI field conventions, not generic placeholder names

**Why this matters for the demo:** This proves operation on real production infrastructure. The tools are SP's actual shipped tooling, not a simulation of what MCP might look like.

---

### Phase 2 — FSM Incident Commander

**What it does:** A Finite State Machine drives a Plan → Act → Observe reasoning loop over the Phase 1 tools to investigate and resolve network incidents autonomously.

**FSM states:**
```
IDLE → TRIAGE → INVESTIGATING → HYPOTHESIZING → REMEDIATING → ESCALATING → RESOLVED
```

**Transition logic (the core product decision):**

| Condition | Transition |
|---|---|
| Confidence ≥ threshold + known remediation path | → `REMEDIATING` |
| Novel anomaly, ambiguous data, or risk above threshold | → `ESCALATING` |
| Dead end after N tool calls | → `ESCALATING` |

**Reference incident (demo scenario):**
> "High packet loss on CI Catalyst Switch in San Jose — interface GigE0/1"

The agent's reasoning chain:
1. `generate_spl` → craft query for interface error counters on target device
2. `run_spl_query` → 30-minute windowed stats (avg errors, drops)
3. `search_indexes` → discover correlated security / ISE logs
4. `run_spl_query` → cross-reference egress traffic by source IP
5. **FSM decision:** if single IP accounts for >60% of egress → flag as potential threat, escalate
6. **Output:** structured JSON summary for human operator or automated remediation stub

**Structured output format:**
```json
{
  "incident_id": "INC-20240214-001",
  "final_state": "ESCALATING",
  "hypothesis": "Potential exfiltration from 10.14.22.87 — 71% of egress traffic",
  "evidence": [
    "2847 out_errors/min spike at 14:32 UTC",
    "No corresponding in_errors (asymmetric)"
  ],
  "tool_calls": 4,
  "recommended_action": "Isolate src_ip=10.14.22.87 pending threat intel confirmation",
  "confidence": 0.84
}
```

**Why FSM and not a free-form agent loop:**

FSMs are auditable and predictable. On live network infrastructure, an agent that takes an unpredictable path is a liability, not an asset. Every state transition is visible, logged, and defensible to an operator. This is an architectural choice made from operational reality — not a simplification. SP's own roadmap presentation (28:10–39:59) describes the journey from "reflex actions" to "autonomous workflows." The FSM is the architecture that makes autonomous workflows trustworthy enough to run on production infrastructure.

---

### Phase 3 — Agent Interaction Evaluator

**What it does:** Scores agent runs on precision, recall, token cost, and tool efficiency. This is a working prototype of SP's roadmap item "Observability for AI agent interactions."

**Two output modes compared:**

| Dimension | Generic (unconstrained) | Schema-enforced (constrained) |
|---|---|---|
| Output format | Verbose natural language | Structured JSON, anomaly-focused |
| Token count | ~11,000 | ~4,200 |
| Actionability | Hedged, general | Specific device + interface + IP |
| Implementation | Base model, no constraints | Same model + strict system prompt + JSON schema |

**Implementation note:** The "constrained" model is not a separately trained model. It is the same base LLM with schema enforcement. This is intentional — it makes the point that prompt engineering and output schemas can cut token usage by 62% without a new model, which is the actual lever available to CI/SP at scale.

**Scoring dimensions:**

| Metric | Definition |
|---|---|
| Precision | Did the output correctly identify the anomalous component? |
| Recall | Did it surface all relevant evidence (errors, traffic spike, suspect IP)? |
| Token cost | `total_tokens × cost_per_1k` — explicit, not abstracted |
| Tool efficiency | Did the agent use the minimum necessary tool calls? |
| Composite score | Weighted combination of the above |

**Why token cost is a first-class metric:**

CI and SP operate at scale. If an investigation that currently costs 11,000 tokens can be reduced to 4,200 tokens through schema enforcement, that difference compounds across tens of thousands of daily incidents. This is not an academic concern — it is a cloud margin problem, and surfacing it explicitly in the evaluator is what differentiates this from a standard AI demo.

---

## What This Directly Addresses on SP's Roadmap

| Roadmap Item | Source | How Vigil Addresses It |
|---|---|---|
| MCP as open protocol for AI-SP integration | SP MCP talk, 13:07–15:31 | Phase 1 built directly on the real GA server |
| Agents: reflex → autonomous workflows | SP MCP talk, 28:10–39:59 | Phase 2 FSM implements this transition with visible state |
| CI Data Fabric + AI platform value | SP MCP talk, 40:18–45:51 | Phase 1 adds CI topology and telemetry tools |
| Enhanced admin controls / permissions | SP MCP talk, 40:18–45:51 | RBAC passthrough in tool registry layer |
| OAuth 2.0 support (upcoming) | SP MCP v1.1.0 roadmap | Architecture stub — documented extension point |
| Observability for AI agent interactions | SP MCP talk, 53:34–54:19 | Phase 3 Evaluator is a working prototype of this feature |

---

## Honest Scope and Limitations

These are known and intentional boundaries, not gaps to be closed:

| Limitation | Why It's Acceptable |
|---|---|
| FSM handles known transitions — struggles with truly novel scenarios | Novel scenarios escalate to human-in-the-loop by design |
| "CI-tuned model" is a constrained prompt, not a trained model | The realistic claim (prompt + schema) is more defensible than pretending a separate model exists |
| Local SP trial means data is synthetic | Architecture is production-ready; data is demo-scale |
| OAuth 2.0 is a documented stub | It's on SP's roadmap, not an Vigil deliverable |

---

## Technical Stack

| Component | Technology |
|---|---|
| Language | Python 3.11+ |
| MCP client | `mcp` Python SDK (Anthropic reference implementation) |
| Agent LLM | Claude via Anthropic API (`claude-opus-4-7` or `claude-sonnet-4-6`) |
| FSM | `transitions` (Python) |
| Schema enforcement | `pydantic` |
| SP connection | Local trial instance; one-line swap to cloud endpoint |
| Evaluation | Custom scoring script, JSON + terminal table output |
| UI | `rich` terminal dashboard |
| Lint / types | `ruff` + `mypy` |
| Tests | `pytest` |

---

## Repository Structure

```
vigil/
├── CLAUDE.md
├── PRD.md                         # this file
├── phase1_mcp/
│   ├── server.py                  # MCP tool definitions (CI additions)
│   ├── tools/
│   │   ├── network_topology.py
│   │   └── telemetry_metrics.py
│   └── config.yaml                # SP endpoint config
├── phase2_agent/
│   ├── commander.py               # FSM + reasoning loop
│   ├── states.py                  # State definitions + transitions
│   ├── prompts.py                 # System prompts per FSM state
│   └── scenarios/
│       └── packet_loss_sj.json    # Reference incident
├── phase3_evaluator/
│   ├── evaluator.py               # Scoring logic
│   ├── models/
│   │   ├── generic.py             # Unconstrained LLM call
│   │   └── constrained.py        # Schema-enforced structured output
│   └── report.py                  # Terminal table + JSON output
└── demo/
    └── console.py                 # Unified war room dashboard
```

---

## Success Criteria

| Phase | Deliverable | Definition of Done |
|---|---|---|
| Phase 1 | MCP connectivity layer | Live connection to SP GA server; both CI tools callable and returning realistic schema |
| Phase 2 | FSM incident commander | Reference scenario (packet loss, San Jose) runs end-to-end; structured JSON output matches spec |
| Phase 3 | Agent evaluator | Scores two model modes on all five dimensions; token cost delta is visible in terminal output |
| Demo | War room console | All three phases visible on one screen; one incident, full lifecycle |

---

## What This Is Not

- A replacement for SP's Troubleshooting Agent (which is scoped to Observability Cloud)
- A claim that the FSM handles all incident types (it handles known transition patterns and escalates the rest)
- A separately trained model (schema enforcement on a base model is the actual mechanism)
- A production-deployed system (this is an architectural reference implementation on a local trial instance)

---

## Bottom Line for the VP

SP shipped the tools. Nobody shipped the brain. Vigil is the brain — an auditable, production-architecture reasoning layer that sits on top of what SP already released, built toward what their own roadmap says is coming next. The five gaps it fills are each citable from SP's own documentation and release notes. The token economics case is quantified, not asserted. And the FSM architecture makes this trustworthy enough to run on live infrastructure — which is the only bar that matters in network operations.

---

*Built to address: MCP integration on real SP infrastructure · FSM-driven agentic reasoning · Model evaluation with cloud margin awareness*
