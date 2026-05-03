"""Score agent runs on precision, recall, and token cost."""
from __future__ import annotations

import anthropic

from phase2_agent.commander import IncidentReport
from phase3_evaluator.models import constrained, generic

# claude-sonnet-4-6 pricing
_COST_INPUT_PER_1K = 0.003
_COST_OUTPUT_PER_1K = 0.015

# Ground truth for the San Jose packet loss incident
_PRECISION_CHECKS: list[tuple[str, list[str]]] = [
    ("device", ["sj-catalyst-01"]),
    ("interface", ["GigE0/1", "GigE 0/1", "gigabitethernet0/1", "gige0/1"]),
    ("threat_ip", ["10.14.22.87"]),
    ("final_state", ["ESCALATING", "escalat"]),
]

_RECALL_CHECKS: list[tuple[str, list[str]]] = [
    ("out_errors", ["out_errors", "output error", "egress error", "2847"]),
    ("spike_time", ["14:30", "14:32"]),
    ("threat_pct", ["71", "70%", "71%"]),
    ("action", ["isolat", "block", "quarantin", "contain"]),
]


def token_cost(input_tokens: int, output_tokens: int) -> float:
    return round(
        (input_tokens / 1000 * _COST_INPUT_PER_1K) + (output_tokens / 1000 * _COST_OUTPUT_PER_1K),
        4,
    )


def _score(text: str, checks: list[tuple[str, list[str]]]) -> float:
    text_lower = text.lower()
    hits = sum(1 for _, keywords in checks if any(kw.lower() in text_lower for kw in keywords))
    return round(hits / len(checks), 3)


def evaluate(report: IncidentReport) -> dict:
    client = anthropic.Anthropic()
    tool_results = [{"tool": r.tool, "result": r.result} for r in report.tool_call_log]

    gen = generic.summarize(report.evidence, tool_results, client)
    con = constrained.summarize(report.evidence, tool_results, client, report.incident_id)

    gen_text = gen["output"]
    con_text = str(con["output"])

    # Score the investigation run itself (hypothesis + evidence)
    inv_text = report.hypothesis + " " + report.recommended_action + " " + " ".join(report.evidence)

    # Tool efficiency: 1.0 if ≤5 calls (optimal), degrades linearly above that
    tool_efficiency = round(max(0.0, 1.0 - max(0, report.tool_calls - 5) * 0.15), 3)

    return {
        "incident_id": report.incident_id,
        "investigation": {
            "final_state": report.final_state,
            "tool_calls": report.tool_calls,
            "total_tokens": report.total_tokens,
            "cost_usd": token_cost(report.input_tokens, report.output_tokens),
            "precision": _score(inv_text, _PRECISION_CHECKS),
            "recall": _score(inv_text, _RECALL_CHECKS),
            "tool_efficiency": tool_efficiency,
            "duration_secs": report.duration_secs,
        },
        "generic": {
            "total_tokens": gen["total_tokens"],
            "cost_usd": token_cost(gen["input_tokens"], gen["output_tokens"]),
            "precision": _score(gen_text, _PRECISION_CHECKS),
            "recall": _score(gen_text, _RECALL_CHECKS),
        },
        "constrained": {
            "total_tokens": con["total_tokens"],
            "cost_usd": token_cost(con["input_tokens"], con["output_tokens"]),
            "precision": _score(con_text, _PRECISION_CHECKS),
            "recall": _score(con_text, _RECALL_CHECKS),
            "output": con["output"],
        },
        "token_savings_pct": round(
            (1 - con["total_tokens"] / max(gen["total_tokens"], 1)) * 100, 1
        ),
    }
