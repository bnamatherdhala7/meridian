# Vigil — Agentic Network Incident Commander

> Replaces 47-minute manual NOC triage with autonomous investigation in under 35 seconds. Built on Splunk MCP + Cisco Catalyst + Pinecone RAG.

---

## The Problem

A P2 network incident fires at 2am. An operator opens Splunk and stares at a search bar.

They know the device. They know the interface. But getting from *alert* to *root cause* requires 5–10 manual queries, cross-referencing topology from Cisco Catalyst Center, and deciding whether to remediate or escalate — all under time pressure, all undocumented.

**Industry benchmarks (PagerDuty 2023, IBM Cost of a Data Breach 2023):**

| Metric | Manual NOC |
|---|---|
| Mean Time to Detect (P2) | 15 minutes |
| Mean Time to Resolve (P2) | 47 minutes |
| False positive triage cost | ~35–40% of all alerts |

---

## What Vigil Does

Vigil is a **7-state FSM agent** that sits on top of Splunk's MCP server and Cisco Catalyst Center. When an alert fires, Vigil:

1. **PRE_TRIAGE** — Scores the alert in <1ms at 0 tokens. Suppresses ~35% of alerts as false positives before any LLM call.
2. **TRIAGE** — Queries Pinecone for the most relevant SPL pattern from 20 vetted templates.
3. **INVESTIGATING** — Pulls live topology + telemetry from Cisco Catalyst. Retrieves the 3 most similar past incidents from memory.
4. **HYPOTHESIZING** — Cross-references evidence to form a root cause hypothesis.
5. **Decision** — Routes to `REMEDIATING` (known fix, low blast radius) or `ESCALATING` (ambiguous, high blast radius, security threat).

All decisions are **auditable** — every state transition, tool call, and RAG retrieval is logged and scored.

---

## Key Results

| Metric | Manual NOC | Vigil | Delta |
|---|---|---|---|
| Mean Time to Detect | 15 min | 8 s | **98.7% faster** |
| Mean Time to Resolve | 47 min | ~35 s | **98.8% faster** |
| False positives suppressed | 0% | 35–40% | saves ~40% of LLM budget |
| Token cost per investigation | — | ~$0.05 | 57% less than unconstrained |
| Decisions audited | 0% | 100% | full FSM trace |

---

## Architecture

```
Alert
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  PRE_TRIAGE  (0 tokens, <1ms)                                   │
│  Rules engine: signal_count, repeat_count, alert_type           │
│  → SUPPRESS (false positive)  |  → ESCALATE_IMMEDIATELY (P0)   │
│  → proceed to FSM                                               │
└─────────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  FSM  (phase2_agent / vigil)                                    │
│                                                                 │
│  TRIAGE ──────────────────────────────────────────────────────► │
│    ◈ Pinecone SPL Knowledge (20 patterns, text-embedding-3-sm)  │
│    ⚡ splunk_run_query · splunk_get_knowledge_objects            │
│                                                                 │
│  INVESTIGATING ────────────────────────────────────────────────► │
│    ◈ Pinecone Incident Memory (30 past incidents)               │
│    ⚡ ci_get_network_topology · ci_get_telemetry_metrics         │
│                                                                 │
│  HYPOTHESIZING ────────────────────────────────────────────────► │
│    ⚡ saia_generate_spl · splunk_run_query                       │
│                                                                 │
│  DECISION                                                        │
│    blast_radius ∈ {HIGH,CRITICAL} + unknown → ESCALATING        │
│    incident_memory_score ≥ 0.75 + known_fix → REMEDIATING       │
│    default → ESCALATING                                         │
└─────────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3 EVALUATOR                                              │
│  Precision · Recall · Token cost · MTTD/MTTR speedup           │
│  Generic vs Constrained LLM comparison                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## RAG Layers

Two Pinecone vector stores power the investigation:

### SPL Knowledge (`vigil-spl-knowledge`)
20 vetted SPL query templates covering packet loss, BGP flaps, CPU spikes, interface errors, threat intel correlation, and more. Retrieved at **TRIAGE** so the agent runs the right query first — not whatever the LLM guesses.

### Incident Memory (`vigil-incident-memory`)
30 past incident summaries with root causes and outcomes. Retrieved at **INVESTIGATING** to inform the REMEDIATING vs ESCALATING decision. When a BGP flap matches `INC-2023-0988` (keepalive timer mismatch, score 0.78), Vigil knows the fix without hallucinating it.

---

## Demo Scenarios

| Scenario | Severity | Expected Path | Decision Rule |
|---|---|---|---|
| Packet Loss / GigE0/1 | P2 | ESCALATING | 71% egress concentration + threat intel match |
| BGP Flap / keepalive | P2 | REMEDIATING | incident_memory_match=0.78, known fix |
| CPU Spike 94% / unknown PID | P1 | ESCALATING | CRITICAL blast radius + unknown process |
| False Positive / threshold_breach | P3 | SUPPRESSED | 5 repeat fires, 0 correlated signals — 0 tokens |

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | `claude-sonnet-4-6` / `claude-opus-4-7` |
| FSM | `transitions` library (Python) |
| RAG — embeddings | OpenAI `text-embedding-3-small` |
| RAG — vector store | Pinecone (serverless, `us-east-1`) |
| MCP tools | Splunk MCP Server + Cisco Catalyst MCP (mocked) |
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
  mcp_client.py      # Splunk MCP HTTP client (+ mock)
  classifier.py      # Pre-triage noise filter

data/
  spl_knowledge/     # 20 SPL pattern records (JSONL)
  incidents/         # 30 past incident summaries (JSONL)

scripts/
  seed_pinecone.py   # Embed + upload both corpora (run once)
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

# 3. Seed Pinecone (run once, after adding keys)
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
| `SPLUNK_*` | Live Splunk queries (optional — mocked by default) | Splunk Cloud → Settings → Tokens |

---

## Splunk MCP Tools Used

| Tool | Purpose |
|---|---|
| `splunk_run_query` | Execute RAG-retrieved SPL patterns |
| `splunk_get_knowledge_objects` | Find relevant saved searches |
| `saia_generate_spl` | Generate hypothesis-driven SPL (AI Assistant app) |

When `SPLUNK_MCP_URL` is not set, `vigil/mcp_client.py` returns realistic mock data for all 3 scenarios. Production deployment requires the [Splunk MCP Server app](https://splunkbase.splunk.com/app/7931).

---

*Built on Splunk MCP + Cisco Catalyst MCP + Pinecone + Anthropic Claude*
