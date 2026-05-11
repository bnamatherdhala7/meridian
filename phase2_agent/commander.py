"""Incident Commander — FSM-driven reasoning loop using Claude tool_use."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable

import anthropic
from transitions import Machine

from phase1_mcp.tools.ci import get_network_topology, get_telemetry_metrics
from phase1_mcp.tools.sp import (
    generate_spl,
    get_knowledge_objects,
    get_metadata,
    get_user_context,
    run_spl_query,
    search_indexes,
)
from phase2_agent.pre_triage import AlertReScorer
from phase2_agent.prompts import STATE_PROMPTS
from phase2_agent.states import STATES, TRANSITIONS, VALID_TRANSITIONS

_TOOL_DEFINITIONS: list[dict] = [
    {
        "name": "run_spl_query",
        "description": "Execute an SPL query against Splunk (splunk_run_query). Returns matching events and statistics.",
        "input_schema": {
            "type": "object",
            "properties": {
                "spl": {"type": "string", "description": "The SPL query to execute"},
                "index": {"type": "string", "description": "Target index (default: *)"},
                "time_window": {"type": "string", "description": "e.g. 'last 30 minutes'"},
            },
            "required": ["spl"],
        },
    },
    {
        "name": "generate_spl",
        "description": "Generate an optimized SPL query from a natural language description (saia_generate_spl).",
        "input_schema": {
            "type": "object",
            "properties": {
                "natural_language": {"type": "string"},
                "index": {"type": "string", "default": "network_telemetry"},
            },
            "required": ["natural_language"],
        },
    },
    {
        "name": "search_indexes",
        "description": "Discover available Splunk indexes and their metadata (splunk_get_indexes).",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
        },
    },
    {
        "name": "get_knowledge_objects",
        "description": "Surface saved searches, field extractions, and lookups from Splunk (splunk_get_knowledge_objects).",
        "input_schema": {
            "type": "object",
            "properties": {"object_type": {"type": "string"}},
        },
    },
    {
        "name": "get_metadata",
        "description": "Discover which hosts are generating events in Splunk indexes (splunk_get_metadata). Use in TRIAGE to identify which devices have active alerts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "index": {"type": "string", "description": "Index to query (default: *)"},
                "metadata_type": {"type": "string", "description": "hosts, sources, or sourcetypes"},
            },
        },
    },
    {
        "name": "get_user_context",
        "description": "Check if a suspect src_ip belongs to a known corporate user (splunk_get_user_info). Use during INVESTIGATING when a single IP shows anomalous traffic.",
        "input_schema": {
            "type": "object",
            "properties": {
                "src_ip": {"type": "string", "description": "IP address to look up"},
                "username": {"type": "string", "description": "Optional username to look up"},
            },
        },
    },
    {
        "name": "get_network_topology",
        "description": "Get CI Catalyst network topology — device graph, uplinks, VLANs, and blast radius.",
        "input_schema": {
            "type": "object",
            "properties": {
                "site": {"type": "string"},
                "device_id": {"type": "string"},
            },
        },
    },
    {
        "name": "get_telemetry_metrics",
        "description": "Get real-time interface-level and device-level telemetry from a CI Catalyst device. Omit interface to get CPU/memory device metrics.",
        "input_schema": {
            "type": "object",
            "properties": {
                "device_id": {"type": "string"},
                "interface": {"type": "string"},
                "time_window": {"type": "string"},
            },
            "required": ["device_id"],
        },
    },
]

_TOOL_FUNCTIONS: dict[str, Any] = {
    "run_spl_query": run_spl_query,
    "generate_spl": generate_spl,
    "search_indexes": search_indexes,
    "get_knowledge_objects": get_knowledge_objects,
    "get_metadata": get_metadata,
    "get_user_context": get_user_context,
    "get_network_topology": get_network_topology,
    "get_telemetry_metrics": get_telemetry_metrics,
}

# Tools available per state — Claude can only call what's relevant
_STATE_TOOL_ALLOWLIST: dict[str, list[str]] = {
    "TRIAGE":        ["search_indexes", "get_metadata", "get_network_topology"],
    "INVESTIGATING": ["get_telemetry_metrics", "run_spl_query", "get_user_context"],
    "HYPOTHESIZING": [],
    "REMEDIATING":   [],
    "ESCALATING":    [],
}

_FSM_TRIGGER: dict[str, str] = {
    "INVESTIGATING": "begin_investigation",
    "HYPOTHESIZING": "form_hypothesis",
    "REMEDIATING": "remediate",
    "ESCALATING": "escalate",
    "RESOLVED": "resolve",
}

# Tighter output caps per state — terminal states need one short sentence, not 2 k tokens
_STATE_MAX_TOKENS: dict[str, int] = {
    "TRIAGE":        512,
    "INVESTIGATING": 1024,
    "HYPOTHESIZING": 512,
    "REMEDIATING":   512,
    "ESCALATING":    512,
}

# Per-state model tiering (Lever 2). Haiku 4.5 handles tool orchestration in
# TRIAGE/INVESTIGATING at ~3x lower input cost and ~3x lower output cost than
# Sonnet 4.6. HYPOTHESIZING — where the actual root-cause decision and FSM
# transition rationale are produced — stays on Sonnet for quality. Terminal
# states do not call the LLM (the loop exits) so their model is moot.
_DEFAULT_REASONING_MODEL = "claude-sonnet-4-6"
_DEFAULT_ROUTING_MODEL   = "claude-haiku-4-5-20251001"

_STATE_MODEL: dict[str, str] = {
    "TRIAGE":        _DEFAULT_ROUTING_MODEL,
    "INVESTIGATING": _DEFAULT_ROUTING_MODEL,
    "HYPOTHESIZING": _DEFAULT_REASONING_MODEL,
    "REMEDIATING":   _DEFAULT_ROUTING_MODEL,
    "ESCALATING":    _DEFAULT_ROUTING_MODEL,
}

# USD per million tokens — Anthropic public pricing.
# Cache write costs 1.25x normal input; cache read costs 0.1x normal input.
_PRICING: dict[str, dict[str, float]] = {
    "sonnet": {"input": 3.00, "output": 15.00},
    "haiku":  {"input": 1.00, "output":  5.00},
}


def compute_run_cost_usd(
    *,
    haiku_input_tokens: int,
    haiku_output_tokens: int,
    sonnet_input_tokens: int,
    sonnet_output_tokens: int,
    cache_creation_input_tokens: int = 0,
    cache_read_input_tokens: int = 0,
) -> dict[str, float]:
    """Compute true API cost for a Vigil run accounting for model tiering and cache.

    Returns breakdown so the evaluator can show where the cost lands.
    """
    # Per-model input prices assume cache breakpoints stay within the same model
    # (true for Vigil — caching is on system+tools within one state, one model).
    # Subtract cache tokens from the per-model input bucket before pricing, then
    # reprice them at the discounted/premium cache rate.

    def _price(model: str, input_tokens: int, output_tokens: int) -> dict[str, float]:
        p = _PRICING[model]
        return {
            "input_usd":  input_tokens  * p["input"]  / 1_000_000,
            "output_usd": output_tokens * p["output"] / 1_000_000,
        }

    # Distribute cache tokens proportionally between models for cost modeling.
    # In practice for Vigil HYPOTHESIZING is Sonnet, others Haiku — the cache
    # tokens land on whichever model owned the state at write/read time.
    # We approximate by ratio of input tokens.
    total_input = haiku_input_tokens + sonnet_input_tokens or 1
    haiku_share  = haiku_input_tokens  / total_input
    sonnet_share = sonnet_input_tokens / total_input

    # Treat cached tokens as already included in haiku/sonnet input counts (we
    # bucketed them into the per-model input total at call time). Subtract them
    # back out, then reprice at cache rates.
    haiku_normal_in  = max(0, haiku_input_tokens  - int(haiku_share  * (cache_creation_input_tokens + cache_read_input_tokens)))
    sonnet_normal_in = max(0, sonnet_input_tokens - int(sonnet_share * (cache_creation_input_tokens + cache_read_input_tokens)))

    haiku_cost  = _price("haiku",  haiku_normal_in,  haiku_output_tokens)
    sonnet_cost = _price("sonnet", sonnet_normal_in, sonnet_output_tokens)

    # Cache pricing — same input price as the model that wrote/read it, scaled
    # by 1.25 (write) and 0.1 (read). Use a blended rate weighted by per-model share.
    blended_input_rate = (
        haiku_share  * _PRICING["haiku"]["input"]
        + sonnet_share * _PRICING["sonnet"]["input"]
    )
    cache_write_usd = cache_creation_input_tokens * blended_input_rate * 1.25 / 1_000_000
    cache_read_usd  = cache_read_input_tokens     * blended_input_rate * 0.10 / 1_000_000

    total_usd = (
        haiku_cost["input_usd"]  + haiku_cost["output_usd"]
        + sonnet_cost["input_usd"] + sonnet_cost["output_usd"]
        + cache_write_usd + cache_read_usd
    )

    return {
        "haiku_input_usd":   haiku_cost["input_usd"],
        "haiku_output_usd":  haiku_cost["output_usd"],
        "sonnet_input_usd":  sonnet_cost["input_usd"],
        "sonnet_output_usd": sonnet_cost["output_usd"],
        "cache_write_usd":   cache_write_usd,
        "cache_read_usd":    cache_read_usd,
        "total_usd":         total_usd,
    }


def _compress_tool_result(tool_name: str, result: dict) -> str:
    """Compact one-liner for a tool result — stored in message history after the first use.

    Full result stays in ToolCallRecord for the evaluator / UI.
    This version is only what gets re-sent on every subsequent API call.
    """
    if tool_name == "search_indexes":
        names = [i.get("name", "") for i in result.get("indexes", [])]
        return f"indexes={','.join(names)}"

    if tool_name == "get_network_topology":
        device = result.get("device_id", "?")
        role   = result.get("role", "?")
        anomalous = [i["name"] for i in result.get("interfaces", []) if i.get("anomaly")]
        uplinks   = [i["name"] for i in result.get("interfaces", []) if i.get("role") == "uplink"]
        return f"{device}({role}) anomalous={anomalous} uplinks={uplinks}"

    if tool_name == "get_telemetry_metrics":
        device = result.get("device_id", "?")
        iface  = result.get("interface", "?")
        m      = result.get("metrics", {})
        return (
            f"{device} {iface}: out_errors={m.get('out_errors',0)} "
            f"in_errors={m.get('in_errors',0)} util={m.get('utilization_pct',0)}% "
            f"drops={m.get('drops',0)} anomaly={result.get('anomaly',False)}"
        )

    if tool_name == "run_spl_query":
        events = result.get("events", [])
        stats  = result.get("stats", {})
        count  = result.get("result_count", len(events))
        lines  = [f"result_count={count}"]
        for e in events[:2]:
            kv = " ".join(f"{k}={v}" for k, v in list(e.items())[:6])
            lines.append(kv)
        # Always include key stats fields — safe_fix, cause, note are decision-critical
        for key in ("safe_fix", "cause", "root_cause", "is_security_threat", "anomaly", "note", "flap_count"):
            if key in stats:
                lines.append(f"stats.{key}={str(stats[key])[:80]}")
        return " | ".join(lines)[:400]

    if tool_name == "get_metadata":
        hosts = [h.get("host", "") for h in result.get("hosts", []) if h.get("has_alerts")]
        return f"alert_hosts={hosts}"

    if tool_name == "get_user_context":
        ip = result.get("src_ip", "?")
        return f"{ip} known={result.get('is_known')} threat={result.get('threat_intel','none')[:60]}"

    return str(result)[:200]


def _reset_context(scenario: dict, tool_call_log: list["ToolCallRecord"], hypothesis: str) -> list[dict]:
    """Collapse accumulated message history into a single compact context message.

    Called on every state transition to prevent quadratic token growth.
    The new state's first API call receives incident facts + compact tool summaries
    instead of the full multi-turn conversation from the previous state.
    """
    lines: list[str] = [
        f"Incident: {scenario['incident_id']} | "
        f"Device: {scenario.get('device','?')} | "
        f"Interface: {scenario.get('interface','?')} | "
        f"Site: {scenario.get('site','?')}",
        f"Description: {scenario.get('description','')}",
    ]
    if tool_call_log:
        lines.append("Tool findings:")
        for r in tool_call_log:
            lines.append(f"  {r.tool}: {_compress_tool_result(r.tool, r.result)}")
    if hypothesis:
        lines.append(f"Hypothesis so far: {hypothesis}")
    return [{"role": "user", "content": "\n".join(lines)}]


@dataclass
class ToolCallRecord:
    tool: str
    input: dict
    result: dict
    duration_ms: int


@dataclass
class IncidentReport:
    incident_id: str
    final_state: str
    hypothesis: str
    evidence: list[str]
    tool_calls: int
    tool_call_log: list[ToolCallRecord]
    recommended_action: str
    confidence: float
    total_tokens: int
    input_tokens: int
    output_tokens: int
    duration_secs: float
    incident_description: str = ""
    # Lever 1: prompt caching — cache_creation costs 1.25x normal input price,
    # cache_read costs 0.1x normal (90% discount). Tracked separately so the
    # evaluator can compute true API cost rather than naive tokens × price.
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0
    # Lever 2: model tiering — Haiku for routing states, Sonnet for reasoning.
    # Per-model token counts so cost calculation uses the right price.
    haiku_input_tokens: int = 0
    haiku_output_tokens: int = 0
    sonnet_input_tokens: int = 0
    sonnet_output_tokens: int = 0


class IncidentCommander:
    def __init__(self, model: str = "claude-sonnet-4-6", max_tool_calls: int = 6) -> None:
        self.model = model
        self.max_tool_calls = max_tool_calls
        self.client = anthropic.Anthropic()

        self.machine = Machine(
            model=self,
            states=STATES,
            transitions=TRANSITIONS,
            initial="IDLE",
            ignore_invalid_triggers=True,
        )

        self.tool_call_log: list[ToolCallRecord] = []
        self.evidence: list[str] = []
        self.hypothesis = ""
        self.confidence = 0.0
        self.recommended_action = ""
        self.total_tokens = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.cache_creation_input_tokens = 0
        self.cache_read_input_tokens = 0
        self.haiku_input_tokens = 0
        self.haiku_output_tokens = 0
        self.sonnet_input_tokens = 0
        self.sonnet_output_tokens = 0

    def _get_tools(self) -> list[dict]:
        allowlist = _STATE_TOOL_ALLOWLIST.get(self.state)
        if allowlist is not None:
            tools = [t for t in _TOOL_DEFINITIONS if t["name"] in allowlist]
        else:
            tools = list(_TOOL_DEFINITIONS)

        valid_next = VALID_TRANSITIONS.get(self.state, [])
        transition_tool: dict = {
            "name": "transition_state",
            "description": "Transition the FSM to the next state. Call when you have enough evidence.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "next_state": {
                        "type": "string",
                        "enum": valid_next,
                        "description": f"Target state. Valid from {self.state}: {valid_next}",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Evidence-backed rationale — name specific device/IP/metrics",
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence 0.0–1.0",
                    },
                },
                "required": ["next_state", "reason", "confidence"],
            },
        }
        return tools + [transition_tool]

    def _call_tool(self, name: str, kwargs: dict) -> dict:
        fn = _TOOL_FUNCTIONS.get(name)
        if fn is None:
            return {"error": f"Unknown tool: {name}"}
        try:
            clean = {k: v for k, v in kwargs.items() if v is not None}
            return fn(**clean)
        except Exception as exc:
            return {"error": str(exc)}

    def _apply_transition(self, inp: dict) -> None:
        next_state = inp.get("next_state", "")
        reason = inp.get("reason", "")
        conf = float(inp.get("confidence", 0.5))

        trigger = _FSM_TRIGGER.get(next_state)
        if trigger:
            getattr(self, trigger)()

        if reason:
            self.hypothesis = reason
        self.confidence = conf
        if reason and next_state in ("ESCALATING", "REMEDIATING"):
            self.evidence.append(reason)
        if next_state in ("ESCALATING", "REMEDIATING") and not self.recommended_action:
            self.recommended_action = reason

    def run(
        self,
        scenario: dict,
        callback: Callable[[str, Any], None] | None = None,
    ) -> IncidentReport:
        start = time.time()

        # PRE_TRIAGE: rules-based re-scoring, 0 tokens
        # Run when scenario carries raw alert data; skip for legacy investigation scenarios.
        pre_triage_result = None
        if "alert" in scenario:
            self.start_pre_triage()
            if callback:
                callback("state_change", {"state": self.state})
            scorer = AlertReScorer()
            pre_triage_result = scorer.score(scenario["alert"])
            if callback:
                callback("pre_triage", {"result": pre_triage_result.model_dump()})

            if pre_triage_result.recommended_action == "suppress":
                self.suppress()
                if callback:
                    callback("state_change", {"state": self.state})
                return IncidentReport(
                    incident_id=scenario["incident_id"],
                    final_state=self.state,
                    hypothesis=pre_triage_result.suppression_reason or "Suppressed by PRE_TRIAGE rules engine",
                    evidence=[pre_triage_result.scoring_rationale],
                    tool_calls=0,
                    tool_call_log=[],
                    recommended_action="suppress",
                    confidence=pre_triage_result.confidence_score,
                    total_tokens=0,
                    input_tokens=0,
                    output_tokens=0,
                    duration_secs=round(time.time() - start, 2),
                    incident_description=scenario.get("description", ""),
                )
            elif pre_triage_result.escalate_immediately:
                self.escalate()
                if callback:
                    callback("state_change", {"state": self.state})
                return IncidentReport(
                    incident_id=scenario["incident_id"],
                    final_state=self.state,
                    hypothesis=pre_triage_result.scoring_rationale,
                    evidence=[pre_triage_result.scoring_rationale],
                    tool_calls=0,
                    tool_call_log=[],
                    recommended_action="escalate — immediate, bypassed FSM investigation",
                    confidence=pre_triage_result.confidence_score,
                    total_tokens=0,
                    input_tokens=0,
                    output_tokens=0,
                    duration_secs=round(time.time() - start, 2),
                    incident_description=scenario.get("description", ""),
                )

        self.start_triage()
        if callback:
            callback("state_change", {"state": self.state})

        messages: list[dict] = [
            {
                "role": "user",
                "content": (
                    f"Investigate this incident:\n\n"
                    f"ID: {scenario['incident_id']}\n"
                    f"Description: {scenario['description']}\n"
                    f"Device: {scenario.get('device', 'unknown')}\n"
                    f"Interface: {scenario.get('interface', 'unknown')}\n"
                    f"Site: {scenario.get('site', 'unknown')}\n"
                    f"Reported at: {scenario.get('reported_at', 'unknown')}"
                ),
            }
        ]

        reset_on_next = False
        while self.state not in ("ESCALATING", "RESOLVED", "SUPPRESSED"):
            if reset_on_next:
                messages = _reset_context(scenario, self.tool_call_log, self.hypothesis)
                reset_on_next = False

            # API requires conversation ends with a user message
            if messages and messages[-1]["role"] == "assistant":
                messages.append({"role": "user", "content": "Continue the investigation."})

            # Lever 2: per-state model tiering. Haiku for routing, Sonnet for reasoning.
            call_model = _STATE_MODEL.get(self.state, self.model)

            # Lever 1: prompt caching. cache_control on the system block caches
            # everything up to and including system (so the tools array — which is
            # static within a state — is also cached). Within a single state's
            # multi-turn loop, all subsequent calls read from cache at 0.1x cost.
            response = self.client.messages.create(
                model=call_model,
                max_tokens=_STATE_MAX_TOKENS.get(self.state, 1024),
                system=[
                    {
                        "type": "text",
                        "text": STATE_PROMPTS[self.state],
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=messages,
                tools=self._get_tools(),
            )

            usage = response.usage
            in_tokens  = getattr(usage, "input_tokens", 0) or 0
            out_tokens = getattr(usage, "output_tokens", 0) or 0
            cache_create = getattr(usage, "cache_creation_input_tokens", 0) or 0
            cache_read   = getattr(usage, "cache_read_input_tokens", 0) or 0

            self.input_tokens  += in_tokens
            self.output_tokens += out_tokens
            self.cache_creation_input_tokens += cache_create
            self.cache_read_input_tokens     += cache_read
            self.total_tokens  += in_tokens + out_tokens + cache_create + cache_read

            # Per-model bucketing — drives accurate cost calculation downstream
            if "haiku" in call_model:
                self.haiku_input_tokens  += in_tokens + cache_create + cache_read
                self.haiku_output_tokens += out_tokens
            else:
                self.sonnet_input_tokens  += in_tokens + cache_create + cache_read
                self.sonnet_output_tokens += out_tokens

            messages.append({"role": "assistant", "content": response.content})

            tool_results: list[dict] = []
            transitioned = False

            for block in response.content:
                if block.type != "tool_use":
                    continue

                if block.name == "transition_state":
                    old_state = self.state
                    self._apply_transition(block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps({"ok": True, "new_state": self.state}),
                    })
                    transitioned = True
                    if callback:
                        callback("state_change", {"from": old_state, "to": self.state})
                    # Schedule context reset for the next iteration.
                    # Resetting here mid-loop would orphan the transition tool_result block.
                    if self.state not in ("ESCALATING", "RESOLVED"):
                        reset_on_next = True
                else:
                    t0 = time.time()
                    result = self._call_tool(block.name, block.input)
                    elapsed = int((time.time() - t0) * 1000)
                    record = ToolCallRecord(block.name, block.input, result, elapsed)
                    self.tool_call_log.append(record)

                    if callback:
                        callback("tool_call", {
                            "tool": block.name,
                            "input": block.input,
                            "result": result,
                            "duration_ms": elapsed,
                            "input_full": json.dumps(block.input, indent=2),
                            "result_full": json.dumps(
                                {k: v for k, v in result.items() if k != "events"}
                                if "events" in result else result,
                                indent=2,
                            ) + (
                                f'\n  "events": [{len(result["events"])} events — see full output]'
                                if "events" in result else ""
                            ),
                        })

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        # Compressed result in message content — enough for the model to reason,
                        # not the full JSON that would bloat the re-sent context on the next call.
                        "content": _compress_tool_result(block.name, result),
                    })

            if tool_results:
                messages.append({"role": "user", "content": tool_results})

            if len(self.tool_call_log) >= self.max_tool_calls and not transitioned:
                self.escalate()
                self.hypothesis = "Max tool calls reached — escalating for human review"
                self.confidence = 0.5
                if callback:
                    callback("state_change", {"state": self.state, "reason": "max_tool_calls"})
                break

            if response.stop_reason == "end_turn" and not tool_results:
                if self.state not in ("ESCALATING", "RESOLVED"):
                    self.escalate()
                    self.hypothesis = "Agent reached end_turn without transitioning"
                    self.confidence = 0.4
                break

        description = (
            f"Incident {scenario['incident_id']}: {scenario.get('description', '')}\n"
            f"Device: {scenario.get('device', 'unknown')}  "
            f"Interface: {scenario.get('interface', 'unknown')}  "
            f"Site: {scenario.get('site', 'unknown')}  "
            f"Severity: {scenario.get('severity', 'unknown')}  "
            f"Reported: {scenario.get('reported_at', 'unknown')}"
        )
        return IncidentReport(
            incident_id=scenario["incident_id"],
            final_state=self.state,
            hypothesis=self.hypothesis,
            evidence=self.evidence,
            tool_calls=len(self.tool_call_log),
            tool_call_log=self.tool_call_log,
            recommended_action=self.recommended_action,
            confidence=self.confidence,
            total_tokens=self.total_tokens,
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            duration_secs=round(time.time() - start, 2),
            incident_description=description,
            cache_creation_input_tokens=self.cache_creation_input_tokens,
            cache_read_input_tokens=self.cache_read_input_tokens,
            haiku_input_tokens=self.haiku_input_tokens,
            haiku_output_tokens=self.haiku_output_tokens,
            sonnet_input_tokens=self.sonnet_input_tokens,
            sonnet_output_tokens=self.sonnet_output_tokens,
        )


def main() -> None:
    import argparse
    import pathlib

    parser = argparse.ArgumentParser(description="Run an incident investigation")
    parser.add_argument(
        "--scenario",
        default="phase2_agent/scenarios/packet_loss_sj.json",
        help="Path to scenario JSON",
    )
    args = parser.parse_args()

    scenario = json.loads(pathlib.Path(args.scenario).read_text())
    commander = IncidentCommander()

    def on_event(event_type: str, data: Any) -> None:
        if event_type == "state_change":
            print(f"[FSM] {data}")
        elif event_type == "tool_call":
            print(f"[TOOL] {data['tool']} ({data['duration_ms']}ms)")

    report = commander.run(scenario, callback=on_event)

    print("\n" + "=" * 60)
    print(json.dumps({
        "incident_id": report.incident_id,
        "final_state": report.final_state,
        "hypothesis": report.hypothesis,
        "evidence": report.evidence,
        "tool_calls": report.tool_calls,
        "recommended_action": report.recommended_action,
        "confidence": report.confidence,
        "total_tokens": report.total_tokens,
        "duration_secs": report.duration_secs,
    }, indent=2))


if __name__ == "__main__":
    main()
