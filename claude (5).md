# SP Agentic Ops — Incident Commander

> An MCP-powered agentic system that builds on SP's GA MCP server to deliver the reasoning layer SP's roadmap points toward but hasn't shipped yet.

---

## Project Vision

SP's MCP server (GA Feb 4) delivers the *plumbing* — tools exist, SPL queries run, RBAC is respected. What's missing is the *reasoning layer*: an agent that decides which tools to call, in what order, and when to stop vs. escalate. This project builds that layer across three phases, each with a concrete demo artifact and a direct tie to CI/SP's stated product direction.

The narrative arc across all three phases:

> **Incident arrives → Agent investigates → Output is evaluated → Human is informed or system self-heals**

---

## Phase 1 — The Connectivity Layer (MCP Integration)

### What to build
Connect to the real SP MCP server (GA). Do not mock the tools — use the actual ones SP shipped.

### Available SP MCP tools (use these)
- `run_spl_query` — execute SPL against a SP index
- `generate_spl` — generate optimized SPL from natural language
- `search_indexes` — discover available indexes and data sources
- `get_knowledge_objects` — surface saved searches, field extractions, lookups

### Tools to add (your contribution on top of SP's server)
- `get_network_topology` — mocked CI Catalyst device graph
- `get_telemetry_metrics` — mocked interface-level counters (errors, drops, utilization)

### Key design decisions
- **Stateless tools** for demo reliability — pure request/response, no session state
- **Schema design is the artifact** — use realistic CI field names: `device_id`, `interface`, `vlan`, `time_window`, `error_rate`
- **RBAC passthrough** — honor SP's existing role-based access; agent inherits the user's permissions
- **One-line config swap** — local SP trial for the demo, but architecture supports a real cloud endpoint via env var

### The "wow" factor
This proves you can operate on real production infrastructure (not a sandbox) and that you understand SP's actual tooling, not just the concept of MCP.

---

## Phase 2 — The Agentic Workflow (Incident Commander)

### What to build
A Finite State Machine (FSM) that drives a Plan → Act → Observe reasoning loop using the MCP tools from Phase 1.

### FSM states
```
IDLE → TRIAGE → INVESTIGATING → HYPOTHESIZING → REMEDIATING → ESCALATING → RESOLVED
```

State transitions are the core logic — decide what triggers `REMEDIATING` vs. `ESCALATING`:
- Confidence above threshold + known remediation path → `REMEDIATING`
- Novel anomaly, ambiguous data, or risk above threshold → `ESCALATING`
- Dead end after N tool calls → `ESCALATING`

### Reference incident (demo scenario)
> "High packet loss on CI Catalyst Switch in San Jose — interface GigE0/1"

**Reasoning chain the agent should follow:**
1. `generate_spl` → craft a query for interface error counters on the target device
2. `run_spl_query` → execute it, get 30-min windowed stats (avg errors, drops)
3. `search_indexes` → discover correlated security / ISE logs
4. `run_spl_query` → cross-reference egress traffic by source IP
5. FSM decision: if single IP accounts for >60% of egress → flag as potential threat, escalate
6. Output: structured JSON summary for human operator OR automated remediation stub

### Why FSM (be ready to defend this)
FSMs are auditable and predictable — in network operations you cannot have an agent take an unpredictable path when touching live infrastructure. The FSM is the *right* architectural choice, not just a simplification. It also produces visible state transitions, which makes the demo easier to follow.

### Output format
```json
{
  "incident_id": "INC-20240214-001",
  "final_state": "ESCALATING",
  "hypothesis": "Potential exfiltration from 10.14.22.87 — 71% of egress traffic",
  "evidence": ["2847 out_errors/min spike at 14:32 UTC", "No corresponding in_errors (asymmetric)"],
  "tool_calls": 4,
  "recommended_action": "Isolate src_ip=10.14.22.87 pending threat intel confirmation",
  "confidence": 0.84
}
```

### The "wow" factor
The SP video (28:10–39:59) demonstrates moving from reflex actions to autonomous workflows conceptually. Your demo *implements* that transition explicitly with visible state and reasoning traces — that's the gap you're filling.

---

## Phase 3 — The Evaluator (Agent Interaction Auditor)

### What to build
An evaluation script that scores agent runs on precision, recall, and token cost. Reframe this not as "LLM-as-judge" but as a prototype of SP's upcoming **Observability for AI** feature (roadmap item: 53:34–54:19 of the SP MCP talk).

### Two model outputs to compare

| Dimension | Generic LLM | CI-tuned (constrained) |
|---|---|---|
| Output format | Verbose natural language summary | Structured JSON, anomaly-focused |
| Token count | ~11,000 | ~4,200 |
| Actionability | Hedged, general | Specific device + interface + IP |
| Implementation | Base model, unconstrained | Same model + strict system prompt + schema enforcement |

> **Implementation note:** The "CI model" is not a different model — it's the same base LLM with a strict system prompt that forces structured JSON output. This is more realistic than pretending a separate model exists, and makes the point that *prompt engineering + schema enforcement* can dramatically reduce token waste.

### Scoring dimensions
- **Precision** — did the output correctly identify the anomalous component?
- **Recall** — did it surface all relevant evidence (errors, traffic spike, suspect IP)?
- **Token cost** — `total_tokens × cost_per_1k` — show the math transparently
- **Tool efficiency** — did the agent use the minimum necessary tool calls?
- **Success score** — weighted composite of the above

### The "wow" factor
Token cost is the business metric most candidates ignore. CI/SP operates at scale — every investigation that costs 4,200 tokens instead of 11,000 is real money across tens of thousands of daily incidents. Showing this in a live evaluator signals you understand the *cloud margin* problem, not just the AI problem.

---

## Demo Architecture

```
┌─────────────────────────────────────────────────────┐
│                  War Room Console                    │
│  ┌──────────┐  ┌──────────────────┐  ┌───────────┐  │
│  │ MCP Tool │  │ FSM Incident     │  │ Evaluator │  │
│  │ Registry │  │ Commander        │  │ Panel     │  │
│  │          │  │                  │  │           │  │
│  │ SP   │  │ PLAN→ACT→OBSERVE │  │ Score     │  │
│  │ native + │  │ state machine    │  │ Tokens    │  │
│  │ CI    │  │ reasoning trace  │  │ Precision │  │
│  │ mocked   │  │                  │  │ Recall    │  │
│  └──────────┘  └──────────────────┘  └───────────┘  │
└─────────────────────────────────────────────────────┘
```

A single terminal dashboard (or simple web UI) where all three phases are visible on one incident. This is the demo artifact — not three separate scripts.

---

## Tech Stack

- **Language:** Python 3.11+
- **MCP client:** `mcp` Python SDK (Anthropic's reference implementation)
- **Agent LLM:** Claude via Anthropic API (or any OpenAI-compatible endpoint)
- **FSM library:** `transitions` (Python) — lightweight, readable state definitions
- **SP connection:** Local SP trial instance (free) — one-line config to swap in cloud endpoint
- **Evaluation:** Custom scoring script, outputs JSON + terminal table
- **UI (optional):** Rich (terminal dashboard) or a single-file React artifact

---

## What This Directly Addresses on CI/SP's Roadmap

| Roadmap Item | Where It Appears | How This Project Addresses It |
|---|---|---|
| MCP as open protocol for AI-SP integration | 13:07–15:31 | Phase 1 — built on real GA server |
| Agents: reflex → autonomous workflows | 28:10–39:59 | Phase 2 — FSM implements this transition explicitly |
| CI Data Fabric + AI platform value | 40:18–45:51 | Phase 1 adds CI topology/telemetry tools |
| Enhanced admin controls / permissions | 40:18–45:51 | Tool registry layer with RBAC passthrough |
| OAuth 2.0 support (upcoming) | 40:18–45:51 | Architecture stub — documented as next step |
| Observability for AI agent interactions | 53:34–54:19 | Phase 3 Evaluator is a prototype of this feature |

---

## Honest Scope Limitations (know these for interviews)

- The FSM handles known state transitions well but struggles with truly novel scenarios — this is where human-in-the-loop escalation matters, and that's by design
- "CI Time Series Model" is a constrained prompt, not a separately trained model
- Local SP trial means data is synthetic — the architecture is production-ready, the data is not
- OAuth 2.0 is documented as a stub, not implemented (it's on SP's roadmap, not yours to ship)

---

## Repo Structure (suggested)

```
sp-incident-commander/
├── claude.md                  # this file
├── README.md
├── phase1_mcp/
│   ├── server.py              # MCP tool definitions (CI additions)
│   ├── tools/
│   │   ├── network_topology.py
│   │   └── telemetry_metrics.py
│   └── config.yaml            # SP endpoint config
├── phase2_agent/
│   ├── commander.py           # FSM + reasoning loop
│   ├── states.py              # State definitions + transitions
│   ├── prompts.py             # System prompts for each FSM state
│   └── scenarios/
│       └── packet_loss_sj.json  # Reference incident
├── phase3_evaluator/
│   ├── evaluator.py           # Scoring logic
│   ├── models/
│   │   ├── generic.py         # Unconstrained LLM call
│   │   └── constrained.py     # Schema-enforced structured output
│   └── report.py              # Terminal table + JSON output
└── demo/
    └── console.py             # Single war room dashboard
```

---

*Built to demonstrate: MCP integration on real SP infrastructure · FSM-driven agentic reasoning · Model evaluation with cloud margin awareness*
