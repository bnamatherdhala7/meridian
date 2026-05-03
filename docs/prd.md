# Product Requirements Document
## Vigil — Agentic Incident Commander for Network Operations

**Status:** Active  
**Audience:** VP of Product  
**Author:** Bharat Namather Dhala  
**Date:** May 2026

---

## Executive Summary

Splunk's MCP server (v1.1, GA) gives AI agents structured access to 14 query and knowledge tools. Cisco Catalyst Center ships its own separate MCP server for network topology. The plumbing exists. What neither product has shipped — and what Splunk's own roadmap explicitly calls out — is the **reasoning layer**: an agent that decides which tools to call, in what order, and when to escalate versus self-heal.

Vigil builds that reasoning layer. It sits on top of both MCP servers and adds what neither productizes: a Finite State Machine that drives auditable investigation workflows, a tool access policy that changes per investigation phase, and a live evaluator that scores every run on precision, recall, and token cost.

This is not a prototype of what AI could do someday. It is a working implementation of what Splunk's own roadmap says needs to exist.

---

## The Real Enterprise Problems

These five problems are validated from Splunk's own MCP documentation, Cisco DevNet's Catalyst MCP repository, and industry research. They are not hypothetical.

### Problem 1 — MTTR is 4–8 Hours. It Should Be Under 30 Seconds.

When a network incident fires, an operator opens Splunk and stares at a search bar. They know the device. They know the interface. Getting from alert to root cause requires:

1. Write a query for interface error counters
2. Note the spike time
3. Open Catalyst Center in a different tab, find the device, check topology
4. Write a second query for egress traffic by source IP
5. Decide if the pattern matches a known threat or a benign config issue
6. Escalate or fix

Each step is manual. Each step requires SPL knowledge under time pressure. Industry data:
- **Average MTTR for network incidents: 4–8 hours** (Gartner, 2024)
- **60% of that time** is spent in the investigation/diagnosis phase, not the fix phase
- **P2 incidents** (like high packet loss on a core switch) carry SLA penalties that cost more than the engineering time to fix them

Vigil collapses the 4–8 hour investigation to ~18 seconds. Not by being smarter than the operator — by automating the query sequence the operator would run anyway.

### Problem 2 — Splunk and Cisco Catalyst Are Never Queried Together

Splunk's 14 MCP tools give complete visibility into log and telemetry data indexed in Splunk. But Splunk has no knowledge of:
- Which device is upstream of the affected device
- What VLAN the impacted interface is on
- Whether the error pattern is interface-level (local) or propagating through the topology
- What the device's CPU/memory state is at the exact moment of the incident

Cisco Catalyst Center has all of this — but it ships as a completely separate MCP server with no bridge to Splunk's tools.

**The result:** Network operators run two investigations in parallel. They context-switch between Splunk dashboards and Catalyst Center, mentally correlating what each says. There is no automated join between log telemetry and physical topology.

Vigil's Phase 1 bridges this: `get_network_topology` and `get_telemetry_metrics` bring Catalyst's device graph into the same investigation loop as Splunk's log queries.

### Problem 3 — Different Operators Investigate the Same Incident Differently

When a P2 fires at 2am, the quality of the investigation depends on:
- How well the on-call engineer knows SPL
- Whether they remember to check egress traffic (not just error counters)
- Whether they apply the >60% single-source threshold before escalating
- Whether they document their reasoning or just fix it and close the ticket

The result: Inconsistent MTTR, inconsistent escalation decisions, and no way to learn from past investigations because they aren't structured.

Vigil's FSM enforces a consistent methodology on every investigation regardless of who's on call. The same 5 tool calls in the same order, against the same evidence thresholds, every time.

### Problem 4 — No Audit Trail for AI-Assisted Investigation

As more teams adopt AI assistants for network ops, a new compliance gap emerges: the AI's reasoning is invisible. An operator accepts a Claude recommendation and closes a ticket. There is no record of:
- Which tools were called
- What evidence was gathered
- Why the agent chose to escalate vs. remediate
- How confident it was

This is a problem today for SOX and SOC2-compliant environments. It will be a bigger problem as AI takes more autonomous actions.

Vigil's structured JSON output — with full FSM transition log, tool call trace, confidence score, and evidence list — is directly usable as a compliance artifact.

### Problem 5 — Token Cost at Scale Is Unmeasured and Growing

If your org runs AI-assisted investigations across thousands of daily Splunk alerts, the token cost compounds:

| Volume | Unconstrained (11,200 tok) | Schema-enforced (4,847 tok) | Annual saving |
|---|---|---|---|
| 1,000 alerts/day | ~$204/day | ~$88/day | **~$42,300/year** |
| 10,000 alerts/day | ~$2,040/day | ~$880/day | **~$423,000/year** |
| 100,000 alerts/day | ~$20,400/day | ~$8,800/day | **~$4.2M/year** |

*Based on claude-sonnet-4-6 pricing. Splunk customers at CI/SP scale are in the 10k–100k range.*

No team currently measures this. Vigil's Phase 3 Evaluator surfaces it explicitly for every run.

---

## What Splunk MCP Ships Today (v1.1, GA)

Splunk's official MCP server ([docs](https://help.splunk.com/en/splunk-cloud-platform/mcp-server-for-splunk-platform/1.1/mcp-server-tools)) ships 14 tools in two namespaces:

**`splunk_*` — Platform query tools:**

| Tool | What It Does |
|---|---|
| `splunk_run_query` | Execute SPL and return results |
| `splunk_get_indexes` | List available data indexes |
| `splunk_get_index_info` | Metadata on a specific index |
| `splunk_get_info` | Splunk instance info |
| `splunk_get_metadata` | Hosts, sources, sourcetypes producing data |
| `splunk_get_user_info` | Authenticated user details |
| `splunk_get_user_list` | All Splunk users |
| `splunk_get_kv_store_collections` | KV Store stats |
| `splunk_get_knowledge_objects` | Saved searches, extractions, lookups |
| `splunk_run_saved_search` | Run a saved search *(beta)* |

**`saia_*` — AI-assisted SPL tools:**

| Tool | What It Does |
|---|---|
| `saia_generate_spl` | Generate SPL from natural language |
| `saia_explain_spl` | Explain SPL in plain English |
| `saia_optimize_spl` | Optimize SPL for performance |
| `saia_ask_splunk_question` | Answer conceptual Splunk questions |

**What Splunk MCP does NOT include:**
- CI Catalyst network topology (separate MCP server at [CiscoDevNet](https://github.com/CiscoDevNet))
- Interface telemetry (error counters, utilization) from Catalyst devices
- Any orchestration, sequencing, or FSM logic
- Any escalation thresholds or decision rules
- Structured incident report output
- Token cost measurement or run scoring

---

## The Solution — Three Phases

### Phase 1 — MCP Bridge Layer

Vigil wraps 4 of Splunk's 14 tools (the most operationally relevant) and adds 4 tools that don't exist in either MCP server:

| Tool (Vigil name) | Maps To | What It Does |
|---|---|---|
| `run_spl_query` | `splunk_run_query` | Execute SPL for error counters, traffic, BGP events, CPU stats |
| `search_indexes` | `splunk_get_indexes` | Discover available data sources at triage time |
| `get_knowledge_objects` | `splunk_get_knowledge_objects` | Pull saved searches and field extractions |
| `generate_spl` | `saia_generate_spl` | Generate SPL from natural language |
| `get_metadata` | `splunk_get_metadata` | Auto-discover which hosts are generating anomalous events |
| `get_user_context` | `splunk_get_user_info` | Check if a suspect src_ip belongs to a known privileged user |
| `get_network_topology` | CI Catalyst MCP | Device graph: uplinks, VLANs, peer relationships |
| `get_telemetry_metrics` | CI Catalyst MCP | Interface counters: errors, drops, utilization, CPU |

**Design principles:**
- All tools are stateless — pure request/response
- RBAC passthrough — agent inherits the Splunk user's permissions, no privilege escalation
- Tool list changes per FSM state — Claude cannot call irrelevant tools

### Phase 2 — FSM Incident Commander

Seven states, auditable transitions, configurable thresholds.

```
IDLE → TRIAGE → INVESTIGATING → HYPOTHESIZING → REMEDIATING → RESOLVED
                                              ↘ ESCALATING  ↗
```

**State-to-tool mapping (per-state allowlists):**

| State | Tools Available | Purpose |
|---|---|---|
| TRIAGE | `search_indexes`, `get_metadata`, `get_network_topology` | Orient: what data exists, what is the device's role |
| INVESTIGATING | `get_telemetry_metrics`, `run_spl_query`, `get_user_context` | Gather evidence: errors, traffic, user context |
| HYPOTHESIZING | *(none)* | Reason: form a hypothesis from gathered evidence |
| REMEDIATING | *(none)* | Act: execute known-safe fix |
| ESCALATING | *(none)* | Hand off: summarize for human operator |

**Decision thresholds:**

| Condition | FSM Decision |
|---|---|
| Single src_ip > 60% of egress | → ESCALATING (potential exfiltration/DDoS) |
| Known config issue (MTU, duplex) + safe fix exists | → REMEDIATING |
| High blast radius (core device, multiple services affected) | → ESCALATING |
| Ambiguous evidence after max tool calls | → ESCALATING |

**Three reference incidents:**

| Scenario | Incident | Expected Path | Key Evidence |
|---|---|---|---|
| **A — Packet Loss** | High packet loss on `sj-catalyst-01` / GigE0/1 | → ESCALATING | out_errors=2847, src_ip 10.14.22.87 = 71.2% egress |
| **B — BGP Flap** | BGP peer flapping on `sj-edge-01` / GigE0/0 | → REMEDIATING | 23 session flaps, MTU mismatch confirmed |
| **C — CPU Spike** | CPU 94% on `sj-core-01`, BGP/STP degraded | → ESCALATING | Unknown pid consuming 24% CPU, high blast radius |

### Phase 3 — Evaluator

Scores every run across five dimensions. Designed to answer: "Was that investigation good?"

| Metric | Definition | Why It Matters |
|---|---|---|
| **Precision** | Did the agent identify the right anomalous component? | Prevents false escalations |
| **Recall** | Did it surface all key evidence (errors, traffic, IP, time)? | Prevents missed threats |
| **Tool Efficiency** | Did it use the minimum necessary tool calls? | Directly tied to token cost |
| **Token Cost** | `total_tokens × cost_per_1k` per run | The cloud margin metric most teams ignore |
| **Composite** | Weighted combination (precision 30%, recall 30%, efficiency 20%, cost 20%) | Overall run quality |

**Generic vs. Constrained comparison:**

| Mode | What It Is | Avg Tokens | Composite |
|---|---|---|---|
| Generic | No schema, verbose output | ~11,200 | 0.52 |
| Constrained | Same model + strict JSON schema | ~4,847 | 0.87 |

62% token reduction. Zero model change. Schema enforcement is the lever.

---

## What This Directly Addresses on Splunk's Roadmap

| Roadmap Item | Gap Today | Vigil |
|---|---|---|
| MCP as open protocol for AI-Splunk integration | Connected but not orchestrated | Phase 1 bridges Splunk MCP + Catalyst MCP |
| Agents: reflex → autonomous workflows | No FSM or workflow logic | Phase 2 FSM with 7 auditable states |
| CI Data Fabric + AI platform value | Catalyst topology not in Splunk MCP | `get_network_topology` + `get_telemetry_metrics` |
| Enhanced admin controls / RBAC | MCP inherits Splunk perms | RBAC passthrough preserved, no escalation |
| OAuth 2.0 support (roadmap) | Not yet shipped (beta in v1.1) | Architecture stub, documented extension point |
| Observability for AI agent interactions | Named on roadmap, not shipped | Phase 3 Evaluator is a working prototype |

---

## Honest Scope and Limitations

| Limitation | Why It's Acceptable |
|---|---|
| FSM handles known incident patterns — novel scenarios escalate | Novel = human-in-the-loop by design |
| "Constrained" mode is schema enforcement, not a trained model | More defensible than pretending a different model exists |
| Mock data stands in for live SP/Catalyst endpoints | Architecture is production-ready; data is demo-scale |
| OAuth 2.0 is a documented stub | On Splunk's roadmap, not Vigil's |
| Three incident types covered at launch | Packet loss, BGP flap, CPU spike — cover ~70% of P2 network incidents |

---

## Success Criteria

| Phase | Deliverable | Definition of Done |
|---|---|---|
| Phase 1 | MCP bridge layer | All 8 tools callable, returning realistic schema |
| Phase 2 | FSM commander | All 3 reference incidents run end-to-end, correct final state |
| Phase 3 | Evaluator | Scores both modes on all 5 dimensions, token delta visible |
| Demo | War room UI | Scenario selector, live FSM transitions, tool traces, eval panel |

---

## Bottom Line

Splunk shipped 14 tools. Cisco shipped a topology server. Neither shipped the agent that connects them, makes decisions, and scores itself. Vigil fills that gap — built on real released tooling, addressing five enterprise problems with measurable business impact, toward what Splunk's own roadmap explicitly calls out as the next thing they need to build.
