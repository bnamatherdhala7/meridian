# Vigil — Agentic Incident Commander

> **SP shipped the tools. Nobody shipped the brain.**

Vigil is a Finite State Machine agent that sits on top of SP's MCP server and autonomously investigates network incidents — deciding which tools to call, in what order, and when to escalate vs. self-heal. It then scores its own run on precision, recall, and token cost.

---

## The Problem

When a network incident fires at 2am, an operator opens SP and stares at a search bar.

They know the device. They know the interface. But getting from *alert* to *root cause* requires 5–10 manual queries, cross-referencing topology data from CI Catalyst, and then deciding whether to remediate or escalate — all under time pressure.

Splunk's MCP server ships 14 tools for querying data (`splunk_run_query`, `splunk_get_indexes`, `saia_generate_spl`, and more). Cisco Catalyst Center ships its own separate MCP server for network topology. The gap is **the reasoning layer that connects them**: what to query first, how to interpret the results, and when to act.

---

## Splunk MCP — What Exists, What's Missing, What Vigil Adds

Splunk's MCP server ([GA, v1.1](https://help.splunk.com/en/splunk-cloud-platform/mcp-server-for-splunk-platform/1.1/mcp-server-tools)) ships **14 tools** across two namespaces: `splunk_*` for platform queries and `saia_*` for AI-assisted SPL. Vigil wraps 4 of those tools and adds everything below the line.

### What Splunk MCP ships (14 tools)

| Tool | What It Does |
|---|---|
| `splunk_run_query` | Execute an SPL search and return results |
| `splunk_get_indexes` | List available indexes |
| `splunk_get_index_info` | Detailed metadata on a specific index |
| `splunk_get_info` | Splunk instance info (version, config) |
| `splunk_get_metadata` | Hosts, sources, and sourcetypes metadata |
| `splunk_get_user_info` | Authenticated user details |
| `splunk_get_user_list` | List of all Splunk users |
| `splunk_get_kv_store_collections` | KV Store collection stats |
| `splunk_get_knowledge_objects` | Saved searches, field extractions, lookups |
| `splunk_run_saved_search` | Run a saved search *(beta)* |
| `saia_generate_spl` | Generate SPL from natural language |
| `saia_explain_spl` | Explain an SPL query in plain English |
| `saia_optimize_spl` | Optimize an SPL query for performance |
| `saia_ask_splunk_question` | Answer conceptual questions about SPL |

### What's missing — and what Vigil builds on top

| Capability | Splunk MCP | Gap | Vigil |
|---|:---:|---|:---:|
| **CI network topology** (device graph, uplinks, VLANs) | ❌ | Cisco Catalyst data lives in a separate MCP server — no bridge to Splunk | ✅ `get_network_topology` |
| **CI interface telemetry** (error counters, utilization, drops) | ❌ | `splunk_run_query` can query telemetry *if indexed*, but no typed tool exists | ✅ `get_telemetry_metrics` |
| **Orchestration — which tool to call first** | ❌ | All 14 tools are exposed simultaneously; no guidance on sequence or phase | ✅ FSM drives TRIAGE → INVESTIGATING → HYPOTHESIZING |
| **State-filtered tool access** | ❌ | LLM sees all tools in every turn — wastes tokens, risks wrong calls | ✅ Per-state allowlists; tool list changes each FSM phase |
| **Threshold-based escalation** | ❌ | No decision rules shipped | ✅ `src_ip > 60% egress → ESCALATING` (configurable) |
| **Structured JSON incident report** | ❌ | Output is free-form text | ✅ Pydantic-validated schema |
| **Token cost per run** | ❌ | Not measured or surfaced | ✅ First-class evaluator metric |
| **Precision / recall scoring** | ❌ | No ground-truth eval framework | ✅ Phase 3 Evaluator |
| **Generic vs. constrained model comparison** | ❌ | Not measured | ✅ Side-by-side, same model two ways |
| **RBAC passthrough** | ✅ | — | Preserved — no privilege escalation added |
| **OAuth 2.0** | 🗓 Roadmap | Not yet shipped | Stub documented, ready to wire in |

### SAIA vs. Vigil — Where Each Starts and Stops

SP's `saia_*` tools (SAIA) generate, explain, and optimize SPL. Vigil consumes SAIA's output and picks up exactly where SAIA stops.

| Capability | SAIA (SP built-in) | Vigil |
|---|---|---|
| SPL generation | ✅ NL → query. Asks clarifying questions for ambiguous prompts. | Calls `saia_generate_spl`. Does not re-implement — consumes the output. |
| SPL optimization | ✅ Rewrites queries for performance (GA in v1.4). | Calls `saia_optimize_spl`. No opinion on result quality — passes it through. |
| Query execution | ❌ **Hard stop** — human must copy SPL and run it manually. | ✅ Executes via `splunk_run_query`. This is where Vigil starts adding value. |
| Multi-step reasoning | ❌ **Hard stop** — single-turn. One prompt → one SPL. No chaining. | ✅ FSM drives 5 tool calls across netflow, topology, and security logs. |
| Cross-domain context | ❌ **Hard stop** — Splunk data only. No CI topology or device telemetry. | ✅ Bridges CI Catalyst topology + telemetry into the same investigation loop. |
| Escalate vs. remediate | ❌ **Hard stop** — returns SPL + explanation. Human decides what to do. | ✅ FSM threshold rules route to `REMEDIATING` or `ESCALATING`. |
| Token cost per run | ❌ 3,000 prompt/month org limit surfaced — no per-query cost shown. | ✅ Phase 3 Evaluator scores tokens, cost, precision, and recall per run. |
| SPL quality before execute | ❌ Internal similarity scoring — not exposed to the user. | 🗓 Roadmap — SPL Quality Gate (see Enhancement Roadmap below) |

---

## What Vigil Does

One incident in. Structured decision out.

```
[Incident Alert] → [FSM Investigation] → [Hypothesis] → [Escalate or Remediate]
                        ↑
                  6 tool calls max
                  state-filtered per phase
                  scored against ground truth
```

The agent doesn't just call tools randomly — it follows an auditable Finite State Machine with 7 states. Every transition is logged. Every tool call is justified by the current state's evidence needs.

---

## War Room Dashboard

![Vigil War Room Dashboard](docs/screenshots/warroom.svg)

The React frontend streams live events from the investigation as it runs — FSM state transitions, tool call traces with expand/collapse, evidence collection, and the final evaluator comparison.

---

## System Architecture

![Vigil Architecture](docs/screenshots/architecture.svg)

**Three phases, one pipeline:**

| Phase | What It Does | Output |
|---|---|---|
| **Phase 1 — MCP Layer** | Wraps 4 Splunk MCP tools + adds 2 CI extensions not in Splunk MCP | 6 callable tools, RBAC passthrough |
| **Phase 2 — FSM Commander** | Claude drives a Plan→Act→Observe loop through 7 states | Structured JSON incident report |
| **Phase 3 — Evaluator** | Scores runs on precision, recall, token cost, tool efficiency | Side-by-side generic vs. constrained comparison |

---

## The FSM — Why Not a Free-Form Agent Loop?

On live network infrastructure, an agent that takes an unpredictable path is a liability. The FSM makes every decision visible and auditable:

```
IDLE → TRIAGE → INVESTIGATING → HYPOTHESIZING → REMEDIATING → RESOLVED
                                              ↘ ESCALATING  ↗
```

| State | What Claude Can Call | Decision Rule |
|---|---|---|
| TRIAGE | `splunk_get_indexes`, `get_network_topology` | Confirm data sources + device role |
| INVESTIGATING | `get_telemetry_metrics`, `splunk_run_query` | Gather error counters + traffic data |
| HYPOTHESIZING | *(no tools)* | Form hypothesis from evidence |
| REMEDIATING | *(no tools)* | Execute known-safe fix |
| ESCALATING | *(no tools)* | Single IP >60% egress, or ambiguous data |

**State-filtered tool lists** prevent Claude from calling wrong tools at wrong times — the tool list itself changes per state, not just the prompt.

---

## Reference Incident

> **INC-20240214-001 · P2 · San Jose**  
> High packet loss on Cisco Catalyst `sj-catalyst-01` / `GigE0/1`

The agent's reasoning chain:

```
1. splunk_get_indexes   → confirms network_telemetry, netflow, security_events available   [145ms]
2. get_network_topology → sj-catalyst-01 uplinks to sj-core-01, GigE0/1 on vlan=100       [118ms]
3. get_telemetry_metrics → out_errors=2847, utilization=94.2%, drops=1203 ⚠               [287ms]
4. splunk_run_query (errors) → avg out_errors=2847.3/min, spike started 14:30 UTC ⚠       [421ms]
5. splunk_run_query (egress) → src_ip 10.14.22.87 = 71.2% of egress (threshold: 60%) ⚠   [389ms]
                                                                                            ─────
FSM decision: single IP > 60% → ESCALATING (confidence 0.93)                        total: ~18s
```

Structured output:

```json
{
  "incident_id": "INC-20240214-001",
  "final_state": "ESCALATING",
  "hypothesis": "sj-catalyst-01 GigE0/1: out_errors=2847 spike at 14:30 UTC, src_ip 10.14.22.87 accounts for 71.2% of egress — isolate and escalate for threat intel",
  "tool_calls": 5,
  "confidence": 0.93,
  "recommended_action": "Isolate src_ip=10.14.22.87 pending threat intel confirmation",
  "total_tokens": 4847,
  "duration_secs": 18.4
}
```

---

## Phase 3 — Token Cost as a First-Class Metric

The same base model (`claude-sonnet-4-6`) run two ways:

| Mode | What It Is | Tokens | Cost/Run |
|---|---|---|---|
| Generic (unconstrained) | No schema enforcement | ~11,200 | ~$0.056 |
| Constrained (schema) | Strict system prompt + JSON schema | ~4,847 | ~$0.024 |

**57% token reduction. Zero model change.** Schema enforcement + tight prompts cut token waste without retraining. At CI/SP scale — tens of thousands of daily investigations — this is a real cloud margin problem.

Scoring dimensions:

| Metric | Generic | Constrained |
|---|---|---|
| Precision | 0.55 | 0.91 |
| Recall | 0.75 | 1.00 |
| Tool Efficiency | — | 0.80 |
| Token Cost | 11,200 | 4,847 |
| **Composite** | 0.52 | **0.87** |

---

## Getting Started

```bash
# Install Python deps
pip install -e ".[dev]"

# Set your Anthropic API key
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# Start the FastAPI backend
cd api && uvicorn server:app --reload

# Start the React frontend (separate terminal)
cd ui && npm install && npm run dev

# Open http://localhost:5173 → click "Run Investigation"
```

**CLI only (no UI):**

```bash
# Run Phase 2 directly on the reference incident
python -m phase2_agent.commander --scenario phase2_agent/scenarios/packet_loss_sj.json
```

---

## What This Addresses on Splunk's Roadmap

| Gap | Splunk MCP Today | Vigil |
|---|---|---|
| Orchestration layer | 14 tools exposed with no sequence guidance — LLM decides freely | FSM enforces TRIAGE → INVESTIGATING → HYPOTHESIZING order |
| CI network context | Not in Splunk MCP — lives in a separate Catalyst Center MCP server | `get_network_topology` + `get_telemetry_metrics` bridge the gap |
| Escalation logic | No decision rules — human judgement only | Configurable thresholds (`src_ip > 60% egress → ESCALATING`) |
| Agent observability | Not shipped (named on roadmap) | Phase 3 Evaluator is a working prototype |
| Token economics | Not measured or surfaced | First-class scoring dimension, shown per run |

---

## Tech Stack

- **Python 3.11+** · `anthropic` SDK · `transitions` (FSM) · `pydantic`
- **FastAPI** with Server-Sent Events for real-time streaming
- **React + Vite** frontend with live FSM diagram, tool trace expansion, evaluator panel
- **Claude `claude-sonnet-4-6`** — FSM commander + evaluator

---

## Docs

| File | Purpose |
|---|---|
| [docs/prd.md](docs/prd.md) | VP-level product requirements — market gap, solution, roadmap alignment |
| [CLAUDE.md](CLAUDE.md) | Architecture decisions, hard rules, command reference |
| [phase2_agent/scenarios/packet_loss_sj.json](phase2_agent/scenarios/packet_loss_sj.json) | Reference incident for demo |

---

## Enhancement Roadmap — SAIA Optimization Layer

Three concrete additions Vigil can layer on top of SAIA's output. Not in v1 — documented as the next phase of development.

### 1. SPL Quality Gate — Score Before Execute

SAIA generates SPL but never tells you if it's good. Vigil can intercept generated SPL before calling `splunk_run_query` and score it on three dimensions: structural validity (correct command sequence), field coverage (do referenced fields exist in the target index?), and estimated resource cost (targeted filters vs. full index scan). Queries below threshold are rejected and regenerated — not executed.

```python
# phase1_mcp/spl_gate.py
score_spl(query, target_index) → SPLScore
# Calls saia_optimize_spl first, then scores before execution
# Blocks: structural_score < 0.7 or field_coverage < 0.6
```

### 2. Investigation-Aware SPL — Context Injection

SAIA generates generic SPL from a cold prompt with no awareness of FSM state, prior tool results, or incident metadata. Vigil can prepend investigation context to every `saia_generate_spl` call — current state, prior telemetry readings, target VLAN — making the generated SPL dramatically more targeted and reducing token waste from irrelevant results.

```python
# phase2_agent/prompts.py
build_spl_context(fsm_state, prior_results) → str
# Prepended to every saia_generate_spl call in the FSM loop
```

### 3. SPL Result Interpreter — Close the Loop SAIA Leaves Open

SAIA's hardest stop: it generates and explains SPL but never interprets the results. A human still reads the output and decides what it means. Vigil already does this implicitly in the OBSERVE step — making it explicit as a reusable component produces a structured `Finding` that feeds directly into `HYPOTHESIZING`.

```python
# phase2_agent/result_interpreter.py
interpret(raw_results, incident_context) → Finding
# Finding fields: anomaly_detected, signal_strength, key_values, noise_pct
```

**Bonus — SPL Cache:** SAIA has a 3,000 prompt/month org limit. Batch investigations call `saia_generate_spl` repeatedly for similar incident types (every packet-loss alert generates roughly the same netflow query). A SQLite cache keyed on `(incident_type, device_role, fsm_state)` serves cached SPL for known patterns and calls SAIA only on misses — reducing SAIA prompt consumption 40–60% at scale.

---

## Out of Scope (v1)

- FSM does not handle truly novel scenarios — those escalate to human-in-the-loop by design
- SP trial data is synthetic — architecture is production-ready, data is not
- OAuth 2.0 is a documented stub — it's on SP's roadmap, not Vigil's

---

*SP GA MCP · FSM-driven agentic reasoning · Token cost as a first-class metric*
