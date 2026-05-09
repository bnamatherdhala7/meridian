# Vigil — Agentic Network Incident Commander

> **SP shipped the tools. Nobody shipped the brain.**

Vigil is a Finite State Machine agent that sits on top of Splunk's MCP server and Cisco Catalyst Center. It autonomously investigates network incidents — deciding which tools to call, in what order, and when to escalate vs. self-heal — backed by Pinecone RAG that retrieves vetted SPL patterns and past incident memory at each investigation step.

---

## The Problem

When a network incident fires at 2am, an operator opens Splunk and stares at a search bar.

They know the device. They know the interface. But getting from *alert* to *root cause* requires 5–10 manual queries, cross-referencing topology data from Cisco Catalyst Center, and deciding whether to remediate or escalate — all under time pressure.

**Industry benchmarks (PagerDuty 2023 · IBM Cost of a Data Breach 2023):**

| Metric | Manual NOC |
|---|---|
| Mean Time to Detect (P2) | 15 minutes |
| Mean Time to Resolve (P2) | 47 minutes |
| Alerts that are false positives | 35–40% |

---

## Key Results

| Metric | Manual NOC | Vigil | Delta |
|---|---|---|---|
| Mean Time to Detect | 15 min | 8 s | **98.7% faster** |
| Mean Time to Resolve | 47 min | ~35 s | **98.8% faster** |
| False positives suppressed | 0% | 35–40% | **0 tokens spent** |
| Token cost per investigation | — | ~$0.05 | **57% less than unconstrained** |
| Decisions audited | 0% | 100% | full FSM trace + JSON report |

---

## Splunk MCP — What Ships Today (14 Tools)

Splunk's MCP server ([GA, v1.1](https://help.splunk.com/en/splunk-cloud-platform/mcp-server-for-splunk-platform/1.1/mcp-server-tools)) exposes 14 tools across two namespaces: `splunk_*` for platform queries and `saia_*` for AI-assisted SPL generation.

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
| `saia_generate_spl` | Generate SPL from natural language (SAIA) |
| `saia_explain_spl` | Explain an SPL query in plain English |
| `saia_optimize_spl` | Optimize an SPL query for performance |
| `saia_ask_splunk_question` | Answer conceptual questions about SPL |

### What's missing — and what Vigil adds

| Capability | Splunk MCP | Gap | Vigil |
|---|:---:|---|:---:|
| **CI network topology** (device graph, uplinks, VLANs) | ❌ | Cisco Catalyst data lives in a separate MCP server | ✅ `get_network_topology` |
| **CI interface telemetry** (error counters, utilization, drops) | ❌ | `splunk_run_query` can query telemetry *if indexed*, but no typed tool exists | ✅ `get_telemetry_metrics` |
| **RAG-retrieved SPL patterns** | ❌ | No vector search over vetted query templates | ✅ Pinecone `vigil-spl-knowledge` (20 patterns) |
| **Past incident memory** | ❌ | No retrieval of similar resolved incidents | ✅ Pinecone `vigil-incident-memory` (30 records) |
| **Tool orchestration — what to call first** | ❌ | All 14 tools exposed simultaneously; no sequencing guidance | ✅ FSM drives TRIAGE → INVESTIGATING → HYPOTHESIZING |
| **State-filtered tool access** | ❌ | LLM sees all tools every turn — wastes tokens | ✅ Per-state allowlists; tool list changes each FSM phase |
| **Threshold-based escalation rules** | ❌ | No decision logic shipped | ✅ `src_ip > 60% egress → ESCALATING` (configurable) |
| **Pre-triage noise suppression** | ❌ | Every alert hits the LLM | ✅ Rules engine suppresses 35–40% at 0 tokens |
| **Structured JSON incident report** | ❌ | Free-form text only | ✅ Pydantic-validated schema, SOX-usable |
| **Token cost per run** | ❌ | Not measured or surfaced | ✅ First-class evaluator metric |
| **RBAC passthrough** | ✅ | — | Preserved — no privilege escalation |
| **OAuth 2.0** | 🗓 Roadmap | Not yet shipped | Extension point documented |

---

## SAIA vs. Vigil — Where Each Starts and Stops

Splunk's `saia_*` tools generate, explain, and optimize SPL. Vigil consumes SAIA output and picks up exactly where SAIA stops.

| Capability | SAIA (Splunk built-in) | Vigil |
|---|---|---|
| SPL generation from natural language | ✅ NL → query using RAG. Handles ambiguous prompts. | Calls `saia_generate_spl` — does not re-implement |
| SPL performance optimization | ✅ Rewrites queries for scan efficiency | Calls `saia_optimize_spl` before executing |
| Query execution | ❌ **Hard stop** — human must run queries manually | ✅ Executes via `splunk_run_query` and interprets results |
| Multi-step reasoning | ❌ **Hard stop** — single-turn. One prompt → one SPL | ✅ FSM chains 5 tool calls across netflow, topology, security |
| Cross-domain context (CI + SP) | ❌ **Hard stop** — Splunk data only | ✅ Bridges Cisco Catalyst topology + telemetry into the loop |
| Escalate vs. remediate decision | ❌ **Hard stop** — returns SPL + explanation only | ✅ Threshold rules route to `REMEDIATING` or `ESCALATING` |
| Past incident retrieval | ❌ No incident memory | ✅ Pinecone retrieves top-3 similar past incidents |
| Per-run cost + quality scoring | ❌ Org-level limit only — no per-query insight | ✅ Precision, recall, token cost, and efficiency every run |

---

## Cisco Catalyst MCP Tools

Vigil adds two tools that bridge CI Catalyst Center data into the Splunk investigation loop:

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
Returns live interface-level and device-level telemetry: error counters (CRC, input/output drops), utilization percentage, BGP state, CPU/memory, and an anomaly flag.

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

Both tools are **stateless** (pure request/response), **RBAC passthrough**, and production-ready. When `CI_CATALYST_URL` is not set, realistic mock data is returned so the FSM runs end-to-end without a live Catalyst deployment.

---

## The FSM — 7 States, Auditable Transitions

```
IDLE → PRE_TRIAGE → TRIAGE → INVESTIGATING → HYPOTHESIZING → REMEDIATING → RESOLVED
                           ↘                              ↘ ESCALATING  ↗
                         SUPPRESSED
```

| State | Tools Available | Exit Condition |
|---|---|---|
| **PRE_TRIAGE** | *(none — rules engine only)* | score < threshold → SUPPRESSED; score ≥ 0.95 + security type → ESCALATING immediately |
| **TRIAGE** | `splunk_get_indexes`, `get_network_topology` + ◈ SPL RAG | Confirms data sources + device role |
| **INVESTIGATING** | `get_telemetry_metrics`, `splunk_run_query` + ◈ Incident RAG | Gathers error counters + traffic egress |
| **HYPOTHESIZING** | `saia_generate_spl`, `splunk_run_query` | Forms root cause hypothesis |
| **REMEDIATING** | *(none)* | Known-safe fix available + blast radius LOW/MEDIUM |
| **ESCALATING** | *(none)* | Ambiguous evidence, HIGH/CRITICAL blast radius, or security threat |

**State-filtered tool lists** prevent Claude from calling wrong tools at wrong times — the tool list changes per state, not just the prompt.

**Decision rules at HYPOTHESIZING:**

| Condition | FSM Decision | Rationale |
|---|---|---|
| Single source IP > 60% of egress | → ESCALATING | Potential exfiltration or DDoS |
| Known config issue + deterministic fix | → REMEDIATING | Safe to automate; reversible action |
| High blast radius (core device) | → ESCALATING | Risk too high for autonomous action |
| Incident memory match ≥ 0.75 + known fix | → REMEDIATING | Grounded in past resolution — not hallucinated |
| Ambiguous evidence after max tool calls | → ESCALATING | Default to human; never guess on live infrastructure |

---

## RAG Layers — Pinecone-Backed Investigation

Two vector stores make every investigation step evidence-grounded:

### ◈ SPL Knowledge (`vigil-spl-knowledge`)
**20 vetted SPL query templates** covering packet loss, BGP flaps, CPU spikes, interface errors, threat intel correlation, flow anomaly detection, and more. Retrieved at **TRIAGE** so the agent runs the right query first — not whatever the LLM guesses.

- Embedding model: OpenAI `text-embedding-3-small`
- Filtered by FSM phase (`TRIAGE` / `INVESTIGATING` / `HYPOTHESIZING`)
- Returns top-3 patterns with similarity scores

### ◈ Incident Memory (`vigil-incident-memory`)
**30 past incident summaries** with root causes, resolutions, and outcomes (`REMEDIATING` / `ESCALATING`). Retrieved at **INVESTIGATING** to inform the routing decision. When a BGP flap returns `INC-2023-0988` at score 0.78 (keepalive timer mismatch, fix: `set bgp timers 30 90`), Vigil routes REMEDIATING — grounded in real resolution history.

---

## Reference Incident

> **INC-20240214-001 · P2 · San Jose**  
> High packet loss on Cisco Catalyst `sj-catalyst-01` / `GigE0/1`

Investigation trace:

```
PRE_TRIAGE        alert scored 0.78 (high), signal_count=3 → proceed          [<1ms · 0 tokens]
◈ SPL RAG         retrieved: packet_loss_egress (0.63), egress_concentration    [380ms · 0 tokens]
01 topology       sj-catalyst-01 uplinks sj-core-01, GigE0/1 on vlan=100        [118ms]
02 telemetry      out_errors=2847, utilization=94.2%, drops=1203 ⚠              [287ms]
03 run_spl        avg out_errors=2847/min, spike started 14:30 UTC ⚠            [421ms]
◈ Incident RAG    retrieved: INC-2024-0891 (0.84) — exfiltration, ESCALATING    [390ms · 0 tokens]
04 run_spl        src_ip 10.14.22.87 = 71.2% of egress (threshold: 60%) ⚠      [389ms]
05 gen_spl        egress concentration + threat intel join query generated       [612ms]
                                                                                 ──────
FSM: single IP > 60% egress → ESCALATING (confidence 0.93)               total: ~35s
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

## Demo Scenarios

| Scenario | Severity | Expected Path | Decision Rule |
|---|---|---|---|
| Packet Loss / GigE0/1 | P2 | **ESCALATING** | 71% egress concentration + threat intel match |
| BGP Flap / keepalive | P2 | **REMEDIATING** | Incident memory match 0.78, known fix: `set bgp timers` |
| CPU Spike 94% / unknown PID | P1 | **ESCALATING** | CRITICAL blast radius + unknown process with Tor connections |
| False Positive / threshold_breach | P3 | **SUPPRESSED** | 5 repeat fires, 0 correlated signals — 0 tokens, <1ms |

---

## Phase 3 — Token Cost as a First-Class Metric

Same base model (`claude-sonnet-4-6`), two prompting strategies:

| Mode | Description | Tokens | Cost/Run |
|---|---|---|---|
| Generic (unconstrained) | No schema enforcement | ~11,200 | ~$0.056 |
| Constrained (schema) | Strict JSON schema system prompt | ~4,847 | ~$0.024 |

**57% token reduction. Zero model change.** At CI/SP scale — tens of thousands of daily investigations — this is a direct cloud margin problem.

| Metric | Generic | Constrained |
|---|---|---|
| Precision | 0.55 | 0.91 |
| Recall | 0.75 | 1.00 |
| Tool Efficiency | — | 0.80 |
| Composite Score | 0.52 | **0.87** |

---

## Architecture

```
Alert
  │
  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PRE_TRIAGE  (0 tokens, <1ms)                                       │
│  Rules engine: signal_count, repeat_count, alert_type               │
│  → SUPPRESSED (false positive)  |  → ESCALATING (P0 security)       │
│  → proceed to FSM investigation                                     │
└─────────────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  FSM INVESTIGATION                                                  │
│                                                                     │
│  TRIAGE                                                             │
│    ◈ Pinecone SPL Knowledge — top-3 patterns (text-embedding-3-sm)  │
│    ⚡ splunk_get_indexes · get_network_topology                      │
│                                                                     │
│  INVESTIGATING                                                      │
│    ◈ Pinecone Incident Memory — top-3 similar past incidents        │
│    ⚡ get_telemetry_metrics · splunk_run_query                       │
│                                                                     │
│  HYPOTHESIZING                                                      │
│    ⚡ saia_generate_spl · splunk_run_query                           │
│                                                                     │
│  DECISION                                                           │
│    egress > 60% + threat intel  → ESCALATING                       │
│    blast_radius HIGH/CRITICAL   → ESCALATING                       │
│    incident_memory ≥ 0.75       → REMEDIATING                      │
│    default                      → ESCALATING                       │
└─────────────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 3 EVALUATOR                                                  │
│  Precision · Recall · Token cost · MTTD/MTTR speedup               │
│  Generic vs Constrained comparison · Structured JSON report        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | `claude-sonnet-4-6` / `claude-opus-4-7` (Anthropic) |
| FSM | `transitions` library (Python) |
| RAG — embeddings | OpenAI `text-embedding-3-small` |
| RAG — vector store | Pinecone serverless (`us-east-1`) |
| MCP tools — Splunk | Splunk MCP Server v1.1 (GA) |
| MCP tools — Cisco | Catalyst MCP (mocked in dev; real endpoint via `CI_CATALYST_URL`) |
| API | FastAPI + Server-Sent Events |
| UI | React + Vite |

---

## Project Structure

```
phase2_agent/        # FSM incident commander (Anthropic API)
  commander.py       # Plan → Act → Observe loop
  pre_triage.py      # Zero-token alert scoring
  prompts.py         # Per-state system prompts
  scenarios/         # 4 reference incidents (JSON)

phase3_evaluator/    # Scoring and MTTD/MTTR tracking
  evaluator.py       # Precision · recall · token cost
  mttd.py            # MTTD/MTTR vs NOC baseline

vigil/               # RAG-enabled FSM (Pinecone + Splunk MCP)
  fsm.py             # 7-state RAG-informed FSM
  rag.py             # SPLKnowledgeRAG + IncidentMemoryRAG
  mcp_client.py      # Splunk MCP HTTP client (+ realistic mock)
  classifier.py      # Pre-triage noise filter

data/
  spl_knowledge/     # 20 SPL pattern records (JSONL)
  incidents/         # 30 past incident summaries (JSONL)

scripts/
  seed_pinecone.py      # Embed + upload both corpora (run once)
  run_investigation.py  # CLI investigation runner

api/server.py        # FastAPI SSE backend
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

---

## Credential Requirements

| Key | Required for | Where to get |
|---|---|---|
| `ANTHROPIC_API_KEY` | FSM investigation | console.anthropic.com |
| `PINECONE_API_KEY` | RAG vector store | app.pinecone.io |
| `OPENAI_API_KEY` | Embedding generation (seed only) | platform.openai.com |
| `SPLUNK_MCP_URL` + `SPLUNK_TOKEN` | Live Splunk queries (optional — mocked by default) | Splunk Cloud → Settings → Tokens |
| `CI_CATALYST_URL` + `CI_CATALYST_TOKEN` | Live Catalyst topology (optional — mocked by default) | CI DevNet / on-prem Catalyst |

---

## Roadmap — v2

| Item | Description |
|---|---|
| **SPL Quality Gate** | Score generated SPL for structural validity + field coverage before executing against production data |
| **SPL Context Injection** | Prepend current FSM state + prior findings to every `saia_generate_spl` call for more targeted queries |
| **SPL Result Interpreter** | Extract structured signal from raw query output → feeds HYPOTHESIZING directly |
| **SPL Cache** | TTL-based cache for known-pattern queries; reduces SAIA prompt consumption 40–60% |
| **Continuous Memory** | Webhook from ServiceNow/Jira to auto-embed resolved incidents into Pinecone after closure |

---

*Built on Splunk MCP v1.1 · Cisco Catalyst MCP · Pinecone · Anthropic Claude*
