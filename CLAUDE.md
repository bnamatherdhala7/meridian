# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Vigil** (working title: SP Agentic Ops — Incident Commander) is a Python project that builds an agentic reasoning layer on top of SP's GA MCP server. The system automates network incident investigation using a Finite State Machine (FSM) and evaluates agent run quality.

The full specification lives in `claude (5).md`.

---

## Planned Commands

Once the project is initialized, commands will follow this pattern:

```bash
# Install dependencies
pip install -e ".[dev]"

# Run Phase 1 MCP server
python -m phase1_mcp.server

# Run Phase 2 incident commander on reference scenario
python -m phase2_agent.commander --scenario phase2_agent/scenarios/packet_loss_sj.json

# Run Phase 3 evaluator
python -m phase3_evaluator.evaluator --run-id <id>

# Run the unified war room demo
python demo/console.py

# Run tests
pytest

# Lint
ruff check . && mypy .
```

---

## Architecture

### Three-Phase Structure

```
phase1_mcp/          # MCP tool registry — SP native + CI mocked tools
phase2_agent/        # FSM incident commander
phase3_evaluator/    # Scoring: precision, recall, token cost
demo/                # Single war room dashboard combining all three
```

### Phase 1 — MCP Connectivity Layer

`phase1_mcp/server.py` registers MCP tools. SP's native tools (`run_spl_query`, `generate_spl`, `search_indexes`, `get_knowledge_objects`) are used as-is. Two CI tools are added on top:

- `get_network_topology` — mocked CI Catalyst device graph
- `get_telemetry_metrics` — mocked interface counters with realistic field names: `device_id`, `interface`, `vlan`, `time_window`, `error_rate`

All tools are **stateless** (pure request/response). SP connection config lives in `phase1_mcp/config.yaml`; the endpoint is swappable via env var.

### Phase 2 — FSM Incident Commander

`phase2_agent/commander.py` drives a Plan → Act → Observe loop using the `transitions` library.

FSM states:
```
IDLE → TRIAGE → INVESTIGATING → HYPOTHESIZING → REMEDIATING → ESCALATING → RESOLVED
```

Transition rules:
- Confidence ≥ threshold + known remediation path → `REMEDIATING`
- Novel anomaly, ambiguous data, or risk above threshold → `ESCALATING`
- Dead end after N tool calls → `ESCALATING`

`phase2_agent/states.py` holds state definitions. `phase2_agent/prompts.py` holds per-state system prompts. The reference incident (packet loss on CI Catalyst GigE0/1, San Jose) lives in `phase2_agent/scenarios/packet_loss_sj.json`.

**Output is structured JSON** (see spec for schema) — not free-form text.

### Phase 3 — Evaluator

`phase3_evaluator/evaluator.py` scores agent runs on: precision, recall, token cost (`total_tokens × cost_per_1k`), tool efficiency, and a weighted composite.

Two model modes are compared — both use the same base model:
- `models/generic.py`: unconstrained call
- `models/constrained.py`: same model + strict JSON schema system prompt

The key insight: the "CI-tuned" model is **not a different model** — it's the same LLM with schema enforcement. This is intentional.

---

## Key Design Decisions

- **FSM over free-form agent**: Auditable, predictable state transitions are required for live network infrastructure. This is an architectural choice, not a limitation.
- **No mocking SP tools**: Phase 1 connects to the real SP MCP server. Only CI topology/telemetry are mocked.
- **RBAC passthrough**: The agent inherits the SP user's permissions — no privilege escalation in the tool layer.
- **Token cost is a first-class metric**: The evaluator surfaces this explicitly because CI/SP operates at scale.
- **OAuth 2.0 is a documented stub**: It's on SP's roadmap. The architecture should accommodate it but not implement it.

---

## Tech Stack

- Python 3.11+
- `mcp` — Anthropic's MCP Python SDK
- `anthropic` — Claude API (default model: `claude-opus-4-7` or `claude-sonnet-4-6`)
- `transitions` — FSM library
- `rich` — terminal dashboard UI
- `pydantic` — schema enforcement for structured outputs
- `ruff` + `mypy` — lint/type-check
- `pytest` — tests
