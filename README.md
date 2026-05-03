# Vigil — Agentic Incident Commander for SP + CI

**Model:** Claude claude-sonnet-4-6 · **Token reduction:** 11,000 → 4,200 per investigation (62%) · **Stack:** Python · MCP · FSM · Pydantic

SP shipped the tools. Nobody shipped the brain.

Vigil is the reasoning layer that sits on top of SP's GA MCP server — a Finite State Machine that decides which tools to call, in what order, and when to stop vs. escalate. It adds CI topology and telemetry context that SP's tooling doesn't have, then scores every run on precision, recall, and token cost.

> Incident arrives → Agent investigates → Output is evaluated → Human is informed or system self-heals

---

## How It Works

**1. Connect** — Vigil attaches to SP's real GA MCP server. No mocking. Four native tools (`run_spl_query`, `generate_spl`, `search_indexes`, `get_knowledge_objects`) plus two CI extensions (`get_network_topology`, `get_telemetry_metrics`) added on top.

**2. Investigate** — An FSM drives a Plan → Act → Observe loop through seven states. Every transition is logged. Every tool call is justified. The agent builds a hypothesis incrementally — it doesn't guess upfront.

**3. Evaluate** — A scoring layer grades the run. Precision, recall, token cost, tool efficiency. Two model modes compared side-by-side. The token delta is the business metric most teams ignore.

---

## The Three Phases

| Phase | What It Is | Deliverable |
|---|---|---|
| **Phase 1 — MCP Layer** | Connects to SP GA + adds CI tools | Tool registry with 6 callable tools |
| **Phase 2 — FSM Commander** | Drives investigation loop through 7 states | Structured JSON incident report |
| **Phase 3 — Evaluator** | Scores runs on 5 dimensions | Terminal table + JSON report |

---

## Phase 1 — MCP Tool Registry

SP's four native tools used as-is. Two CI tools added on top:

| Tool | Source | What It Returns |
|---|---|---|
| `run_spl_query` | SP GA | SPL query results |
| `generate_spl` | SP GA | Optimized SPL from natural language |
| `search_indexes` | SP GA | Available indexes and data sources |
| `get_knowledge_objects` | SP GA | Saved searches, field extractions, lookups |
| `get_network_topology` | CI (Vigil) | Device graph: `device_id`, `interface`, `vlan` relationships |
| `get_telemetry_metrics` | CI (Vigil) | Interface counters: `error_rate`, `drops`, `utilization` per `time_window` |

All tools are stateless — pure request/response. RBAC passthrough: the agent inherits the SP user's permissions, no privilege escalation in the tool layer.

---

## Phase 2 — FSM Incident Commander

Seven states. Every transition is rule-based, auditable, and logged.

```
IDLE → TRIAGE → INVESTIGATING → HYPOTHESIZING → REMEDIATING → RESOLVED
                                              ↘ ESCALATING
```

### State Transitions

| From | To | Trigger |
|---|---|---|
| IDLE | TRIAGE | Incident received |
| TRIAGE | INVESTIGATING | Incident confirmed, data sources identified |
| INVESTIGATING | HYPOTHESIZING | Evidence collected, pattern emerging |
| HYPOTHESIZING | REMEDIATING | Confidence ≥ 0.75 + known remediation path |
| HYPOTHESIZING | ESCALATING | Novel anomaly, ambiguous data, or risk above threshold |
| INVESTIGATING | ESCALATING | Dead end after N tool calls |
| REMEDIATING | RESOLVED | Remediation confirmed |
| ESCALATING | RESOLVED | Human acknowledged |

### Reference Incident

> "High packet loss on CI Catalyst Switch in San Jose — interface GigE0/1"

The agent's reasoning chain for this scenario:

```
1. generate_spl      → craft query for interface error counters on GigE0/1
2. run_spl_query     → 30-min windowed stats: 2,847 out_errors/min at 14:32 UTC
3. search_indexes    → discover correlated ISE / security logs
4. run_spl_query     → egress traffic by source IP → 10.14.22.87 = 71% of total
5. FSM decision      → single IP > 60% threshold → ESCALATING
```

### Structured Output

```json
{
  "incident_id": "INC-20240214-001",
  "final_state": "ESCALATING",
  "hypothesis": "Potential exfiltration from 10.14.22.87 — 71% of egress traffic",
  "evidence": [
    "2847 out_errors/min spike at 14:32 UTC",
    "No corresponding in_errors (asymmetric — rules out duplex mismatch)"
  ],
  "tool_calls": 4,
  "recommended_action": "Isolate src_ip=10.14.22.87 pending threat intel confirmation",
  "confidence": 0.84
}
```

### Why FSM Over a Free-Form Agent Loop

On live network infrastructure, an agent that takes an unpredictable path is a liability. The FSM makes every decision visible: operators can see exactly which state the system is in, which transition fired, and why. SP's own roadmap presentation (28:10–39:59) describes the journey from "reflex actions" to "autonomous workflows." The FSM is what makes autonomous workflows trustworthy enough to run on production.

---

## Phase 3 — Agent Interaction Evaluator

Scores runs on five dimensions. Reframes LLM-as-judge as a prototype of SP's roadmap item: "Observability for AI agent interactions" (roadmap timestamp: 53:34–54:19).

### Two Model Modes Compared

| Dimension | Generic (unconstrained) | Schema-enforced (constrained) |
|---|---|---|
| Output format | Verbose natural language | Structured JSON, anomaly-focused |
| Token count | ~11,000 | ~4,200 |
| Cost per run | ~$0.056 | ~$0.021 |
| Actionability | Hedged, general | Specific device + interface + IP |
| Implementation | Base model, no constraints | Same model + strict system prompt + Pydantic schema |

**62% token reduction. Zero model change.** The "CI-tuned" mode is not a different model — it's the same base LLM with schema enforcement. Prompt engineering + output schemas cut token waste without retraining anything.

### Scoring Dimensions

| Metric | Definition |
|---|---|
| Precision | Did the output correctly identify the anomalous component? |
| Recall | Did it surface all relevant evidence (errors, traffic spike, suspect IP)? |
| Token cost | `total_tokens × cost_per_1k` — shown explicitly, not abstracted |
| Tool efficiency | Did the agent use the minimum necessary tool calls? |
| Composite | Weighted combination of the above, configurable per deployment |

At CI/SP scale — tens of thousands of investigations daily — the difference between 11,000 and 4,200 tokens per run is a real cloud margin problem. Surfacing it in the evaluator makes the business case visible.

---

## War Room Console

All three phases in one terminal dashboard. One incident, full lifecycle:

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

Not three separate scripts — one unified console that shows an incident move from detection to resolution or escalation in real time.

---

## What This Addresses on SP's Roadmap

| Gap | SP's Current State | Vigil |
|---|---|---|
| Orchestration | No agent decides tool sequence | FSM drives Plan → Act → Observe loop |
| Network context | No CI topology or telemetry | `get_network_topology` + `get_telemetry_metrics` |
| Decision logic | No threshold-based escalation | FSM transitions with configurable thresholds |
| Agent observability | Named as a roadmap item — not shipped | Phase 3 Evaluator is a working prototype |
| Token economics | No cost-aware evaluation | Token cost is a first-class scoring dimension |

---

## Tech Stack

| Component | Technology | Why |
|---|---|---|
| Language | Python 3.11+ | Typing, async, ecosystem |
| MCP client | `mcp` Python SDK | Anthropic's reference implementation |
| Agent LLM | Claude via Anthropic API | `claude-opus-4-7` for reasoning, `claude-sonnet-4-6` for throughput |
| FSM | `transitions` | Readable state definitions, auditable transitions |
| Schema enforcement | `pydantic` | Structured output validation, token reduction |
| SP connection | Local trial → env var swap | `SP_ENDPOINT` + `SP_TOKEN` |
| UI | `rich` | Terminal dashboard, no browser dependency |
| Lint / types | `ruff` + `mypy` | Enforced on commit |
| Tests | `pytest` | Unit + integration |

---

## Getting Started

```bash
# Install
pip install -e ".[dev]"

# Configure SP connection (or leave in mock mode)
export SP_ENDPOINT=https://your-sp-instance:8089
export SP_TOKEN=your-token

# Configure Claude
export ANTHROPIC_API_KEY=your-key

# Run Phase 1 — verify MCP connection
python -m phase1_mcp.server

# Run Phase 2 — reference incident
python -m phase2_agent.commander --scenario phase2_agent/scenarios/packet_loss_sj.json

# Run Phase 3 — score the run
python -m phase3_evaluator.evaluator --run-id <id>

# Run the war room demo
python demo/console.py

# Lint + typecheck
ruff check . && mypy .

# Tests
pytest
```

---

## Investigation Cost by Mode

| Scenario | Model Mode | Tokens | Cost per Run |
|---|---|---|---|
| Packet loss, known pattern | Schema-enforced | ~4,200 | ~$0.021 |
| Packet loss, known pattern | Unconstrained | ~11,000 | ~$0.056 |
| Novel anomaly → ESCALATING | Schema-enforced | ~5,800 | ~$0.029 |
| Novel anomaly → ESCALATING | Unconstrained | ~14,000 | ~$0.070 |

*Costs based on `claude-sonnet-4-6` pricing. Multiply by daily incident volume for cloud margin impact.*

---

## Docs

| File | Purpose |
|---|---|
| [docs/prd.md](docs/prd.md) | VP-level product requirements — market gap, solution, roadmap alignment |
| [CLAUDE.md](CLAUDE.md) | Build spec — architecture decisions, hard rules, command reference |
| [phase2_agent/scenarios/packet_loss_sj.json](phase2_agent/scenarios/packet_loss_sj.json) | Reference incident for demo |

---

## Out of Scope (v1)

- FSM does not handle truly novel scenarios — those escalate to human-in-the-loop by design
- OAuth 2.0 is a documented stub — it's on SP's roadmap, not Vigil's
- SP trial data is synthetic — the architecture is production-ready, the data is not
- The "CI-tuned" mode is prompt + schema, not a separately trained model

---

*Built on SP's GA MCP server · FSM-driven agentic reasoning · Token cost as a first-class metric*
