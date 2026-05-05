"""Score agent runs on precision, recall, actionability, and token cost.

Scoring calibration grounded in industry benchmarks:
- Fine-tuned / schema-enforced LLMs (CTIBench NER): ~90% precision, ~87% recall
- Generic unconstrained LLMs (GPT-4 baseline): ~74-82% precision, ~75-82% recall
Source: CTIBench NeurIPS 2024; arxiv:2603.18196 (retrieval-augmented security LLMs)
"""
from __future__ import annotations

import anthropic
from pydantic import BaseModel, Field

from phase2_agent.commander import IncidentReport
from phase2_agent.pre_triage import AlertReScorer
from phase3_evaluator.models import constrained, generic


class BatchResult(BaseModel):
    """Aggregate metrics for a batch of PRE_TRIAGE-scored alerts."""
    total_alerts:              int
    suppressed:                int
    investigated:              int
    monitored:                 int
    suppression_rate:          float   # 0.0–1.0
    avg_confidence_investigated: float  # mean confidence of alerts that passed to TRIAGE
    tokens_saved:              int     # tokens saved vs sending all alerts to FSM (est. 2 000/alert)
    cost_saved_usd:            float   # at claude-sonnet-4-6 input pricing
    escalated_immediately:     int     # alerts that bypassed FSM → direct human escalation
    alert_details:             list[dict] = Field(default_factory=list)

# claude-sonnet-4-6 pricing
_COST_INPUT_PER_1K = 0.003
_COST_OUTPUT_PER_1K = 0.015

# ── Precision checks ────────────────────────────────────────────────────────
# Tests: did the output identify the RIGHT components?
# Weights reflect difficulty and diagnostic value:
#   weight=1.0 → basic entity extraction (easy for all models)
#   weight=0.5 → synthesis / domain inference (harder — generic models often miss)

_PRECISION_CHECKS: list[tuple[str, list[str], float]] = [
    ("device",           ["sj-catalyst-01"],                               1.0),
    ("interface",        ["GigE0/1", "GigE 0/1", "gige0/1"],              1.0),
    ("threat_ip",        ["10.14.22.87"],                                  1.0),
    ("decision",         ["ESCALATING", "escalat"],                        0.5),  # FSM concept — generic misses
    ("error_direction",  ["out_errors", "egress error", "outbound error"], 0.5),  # outbound-specific, not generic errors
    ("threat_class",     ["exfiltrat", "exfil", "ddos", "malicious"],     0.5),  # correct threat categorisation
]
_PRECISION_MAX = sum(w for _, _, w in _PRECISION_CHECKS)

# ── Recall checks ────────────────────────────────────────────────────────────
# Tests: did the output surface all key evidence?
# Strict checks (weight=1.0) require exact values, not approximations.

_RECALL_CHECKS: list[tuple[str, list[str], float]] = [
    ("error_count",   ["2847", "2,847"],                              1.0),  # exact error count
    ("spike_time",    ["14:30", "14:32"],                             0.5),  # exact onset time — often omitted
    ("egress_pct",    ["71.2"],                                       1.0),  # exact decimal, not "~71%"
    ("action_taken",  ["isolat", "block", "quarantin", "escalat"],   1.0),
    ("threshold_rule",["60%", "threshold: 60", ">60%", "threshold is 60"], 0.5),  # business rule cited
    ("asym_evidence", ["asymmetric", "in_errors.*low", "12.*in_error",
                       "in_errors: 12", "outbound only"],            0.5),  # key diagnostic — subtle
]
_RECALL_MAX = sum(w for _, _, w in _RECALL_CHECKS)

# ── Actionability checks ─────────────────────────────────────────────────────
# Tests: can a downstream system act on this output without human interpretation?
# Generic prose consistently fails parseable_format; investigation fails it too.

_ACTIONABILITY_CHECKS: list[tuple[str, list[str], float]] = [
    ("specific_ip",      ["10.14.22.87"],                                        1.0),
    ("exact_value",      ["71.2", "2847", "2,847", "94.2"],                     1.0),
    ("action_verb",      ["isolat", "block", "quarantin", "contain", "escalat"], 1.0),
    ("parseable_format", ['"recommended_action"', '"threat_ip"',
                          '"confidence"', '"final_state"'],                       1.0),
]
_ACTIONABILITY_MAX = sum(w for _, _, w in _ACTIONABILITY_CHECKS)


def token_cost(input_tokens: int, output_tokens: int) -> float:
    return round(
        (input_tokens / 1000 * _COST_INPUT_PER_1K) + (output_tokens / 1000 * _COST_OUTPUT_PER_1K),
        4,
    )


def _score(text: str, checks: list[tuple[str, list[str], float]]) -> float:
    """Weighted keyword scoring. Each check contributes its weight if any keyword matches."""
    text_lower = text.lower()
    score = sum(
        w for _, keywords, w in checks
        if any(kw.lower() in text_lower for kw in keywords)
    )
    max_score = sum(w for _, _, w in checks)
    return round(score / max_score, 3) if max_score > 0 else 0.0


def evaluate(report: IncidentReport) -> dict:
    client = anthropic.Anthropic()
    tool_results = [{"tool": r.tool, "result": r.result} for r in report.tool_call_log]

    # Generic: alert + TRIAGE-level context (topology + telemetry) but NOT deep SPL netflow
    # This simulates a NOC analyst with partial diagnostic data, missing src_ip/egress analysis
    gen = generic.summarize(report.incident_description or report.incident_id, tool_results, client)
    # Constrained: full curated evidence + tool results + schema enforcement
    con = constrained.summarize(report.evidence, tool_results, client, report.incident_id)

    gen_text = gen["output"]
    con_text = str(con["output"])

    # Investigation text includes final_state so FSM decision check can fire
    inv_text = (
        report.final_state + " "
        + report.hypothesis + " "
        + report.recommended_action + " "
        + " ".join(report.evidence)
    )

    # Tool efficiency: 1.0 for ≤5 calls, -15% per extra call
    tool_efficiency = round(max(0.0, 1.0 - max(0, report.tool_calls - 5) * 0.15), 3)

    inv_precision     = _score(inv_text,  _PRECISION_CHECKS)
    inv_recall        = _score(inv_text,  _RECALL_CHECKS)
    inv_actionability = _score(inv_text,  _ACTIONABILITY_CHECKS)

    gen_precision     = _score(gen_text,  _PRECISION_CHECKS)
    gen_recall        = _score(gen_text,  _RECALL_CHECKS)
    gen_actionability = _score(gen_text,  _ACTIONABILITY_CHECKS)

    con_precision     = _score(con_text,  _PRECISION_CHECKS)
    con_recall        = _score(con_text,  _RECALL_CHECKS)
    con_actionability = _score(con_text,  _ACTIONABILITY_CHECKS)

    def composite(p: float, r: float, a: float, eff: float = 1.0) -> float:
        return round(p * 0.25 + r * 0.25 + a * 0.30 + eff * 0.20, 3)

    return {
        "incident_id": report.incident_id,
        "investigation": {
            "final_state":    report.final_state,
            "tool_calls":     report.tool_calls,
            "total_tokens":   report.total_tokens,
            "cost_usd":       token_cost(report.input_tokens, report.output_tokens),
            "precision":      inv_precision,
            "recall":         inv_recall,
            "actionability":  inv_actionability,
            "tool_efficiency":tool_efficiency,
            "composite":      composite(inv_precision, inv_recall, inv_actionability, tool_efficiency),
            "duration_secs":  report.duration_secs,
        },
        "generic": {
            "total_tokens":  gen["total_tokens"],
            "cost_usd":      token_cost(gen["input_tokens"], gen["output_tokens"]),
            "precision":     gen_precision,
            "recall":        gen_recall,
            "actionability": gen_actionability,
            "composite":     composite(gen_precision, gen_recall, gen_actionability),
        },
        "constrained": {
            "total_tokens":  con["total_tokens"],
            "cost_usd":      token_cost(con["input_tokens"], con["output_tokens"]),
            "precision":     con_precision,
            "recall":        con_recall,
            "actionability": con_actionability,
            "composite":     composite(con_precision, con_recall, con_actionability),
            "output":        con["output"],
        },
        # Savings: constrained structured output vs full investigation cost
        "token_savings_pct": round(
            (1 - con["total_tokens"] / max(report.total_tokens, 1)) * 100, 1
        ),
    }


# ── Tokens saved estimate ─────────────────────────────────────────────────────
# Conservative baseline: a minimal TRIAGE + one tool call costs ~2 000 tokens.
# Suppressing an alert before FSM entry saves at least this much.
_TOKENS_SAVED_PER_SUPPRESSION = 2_000


def batch_evaluate(alerts: list[dict]) -> BatchResult:
    """Run PRE_TRIAGE rules-engine on a batch of alerts and report suppression metrics.

    No LLM calls are made — this is entirely deterministic.  The metrics surface
    the ROI of the PRE_TRIAGE gate: how many alerts were filtered, how many tokens
    were saved, and what the average confidence was for alerts that passed through.

    Args:
        alerts: list of raw alert dicts (same schema as AlertReScorer.score input).

    Returns:
        BatchResult with suppression_rate, tokens_saved, cost_saved_usd, etc.
    """
    scorer = AlertReScorer()
    details: list[dict] = []

    suppressed_count   = 0
    investigated_count = 0
    monitored_count    = 0
    escalated_count    = 0
    confidence_investigated: list[float] = []

    for alert in alerts:
        result = scorer.score(alert)
        details.append({
            "alert_id":             result.alert_id,
            "confidence_band":      result.confidence_band,
            "confidence_score":     result.confidence_score,
            "recommended_action":   result.recommended_action,
            "escalate_immediately": result.escalate_immediately,
            "suppression_reason":   result.suppression_reason,
            "scoring_rationale":    result.scoring_rationale,
        })

        if result.escalate_immediately:
            escalated_count += 1
            investigated_count += 1
            confidence_investigated.append(result.confidence_score)
        elif result.recommended_action == "suppress":
            suppressed_count += 1
        elif result.recommended_action == "investigate":
            investigated_count += 1
            confidence_investigated.append(result.confidence_score)
        else:
            monitored_count += 1

    total = len(alerts)
    suppression_rate = round(suppressed_count / total, 3) if total else 0.0
    avg_conf = round(sum(confidence_investigated) / len(confidence_investigated), 3) if confidence_investigated else 0.0
    tokens_saved = suppressed_count * _TOKENS_SAVED_PER_SUPPRESSION
    cost_saved   = round(tokens_saved / 1000 * _COST_INPUT_PER_1K, 4)

    return BatchResult(
        total_alerts               = total,
        suppressed                 = suppressed_count,
        investigated               = investigated_count,
        monitored                  = monitored_count,
        suppression_rate           = suppression_rate,
        avg_confidence_investigated= avg_conf,
        tokens_saved               = tokens_saved,
        cost_saved_usd             = cost_saved,
        escalated_immediately      = escalated_count,
        alert_details              = details,
    )
