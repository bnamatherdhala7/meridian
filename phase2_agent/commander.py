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
    run_spl_query,
    search_indexes,
)
from phase2_agent.prompts import STATE_PROMPTS
from phase2_agent.states import STATES, TRANSITIONS, VALID_TRANSITIONS

_TOOL_DEFINITIONS: list[dict] = [
    {
        "name": "run_spl_query",
        "description": "Execute an SPL query against SP. Returns matching events and statistics.",
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
        "description": "Generate an optimized SPL query from a natural language description.",
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
        "description": "Discover available SP indexes and their metadata.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
        },
    },
    {
        "name": "get_knowledge_objects",
        "description": "Surface saved searches, field extractions, and lookups from SP.",
        "input_schema": {
            "type": "object",
            "properties": {"object_type": {"type": "string"}},
        },
    },
    {
        "name": "get_network_topology",
        "description": "Get CI Catalyst network topology — device graph and links.",
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
        "description": "Get real-time interface-level telemetry metrics from a CI device.",
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
    "get_network_topology": get_network_topology,
    "get_telemetry_metrics": get_telemetry_metrics,
}

# Tools available per state — Claude can only call what's relevant
_STATE_TOOL_ALLOWLIST: dict[str, list[str]] = {
    "TRIAGE":        ["search_indexes", "get_network_topology"],
    "INVESTIGATING": ["get_telemetry_metrics", "run_spl_query"],
    "HYPOTHESIZING": ["run_spl_query"],
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

        from_state = self.state  # capture before FSM trigger mutates self.state

        trigger = _FSM_TRIGGER.get(next_state)
        if trigger:
            getattr(self, trigger)()

        self.hypothesis = reason
        self.confidence = conf
        # Add evidence only on final decisions (→ ESCALATING or → REMEDIATING)
        # This excludes intermediate TRIAGE→INVESTIGATING and INVESTIGATING→HYPOTHESIZING noise
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

        while self.state not in ("ESCALATING", "RESOLVED"):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=STATE_PROMPTS[self.state],
                messages=messages,
                tools=self._get_tools(),
            )

            self.input_tokens += response.usage.input_tokens
            self.output_tokens += response.usage.output_tokens
            self.total_tokens += response.usage.input_tokens + response.usage.output_tokens

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
                        "content": json.dumps(result),
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
