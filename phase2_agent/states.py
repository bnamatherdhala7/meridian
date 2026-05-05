"""FSM state and transition definitions."""
from __future__ import annotations

STATES = [
    "IDLE",
    "PRE_TRIAGE",    # Rules-based re-scorer (0 tokens) — new first state
    "TRIAGE",
    "INVESTIGATING",
    "HYPOTHESIZING",
    "REMEDIATING",
    "ESCALATING",
    "RESOLVED",
    "SUPPRESSED",    # Terminal: alert scored low-confidence, not worth investigating
]

TRANSITIONS = [
    {"trigger": "start_pre_triage",  "source": "IDLE",                    "dest": "PRE_TRIAGE"},
    # PRE_TRIAGE exits
    {"trigger": "start_triage",      "source": ["PRE_TRIAGE", "IDLE"],    "dest": "TRIAGE"},  # IDLE→TRIAGE for legacy scenarios
    {"trigger": "suppress",          "source": "PRE_TRIAGE",              "dest": "SUPPRESSED"},
    {
        "trigger": "escalate",
        "source": ["PRE_TRIAGE", "TRIAGE", "INVESTIGATING", "HYPOTHESIZING", "REMEDIATING"],
        "dest": "ESCALATING",
    },
    {"trigger": "begin_investigation", "source": "TRIAGE",        "dest": "INVESTIGATING"},
    {"trigger": "form_hypothesis",     "source": "INVESTIGATING", "dest": "HYPOTHESIZING"},
    {"trigger": "remediate",           "source": "HYPOTHESIZING", "dest": "REMEDIATING"},
    {"trigger": "resolve",             "source": ["REMEDIATING", "ESCALATING"], "dest": "RESOLVED"},
]

# Valid next states from each state — used to constrain the transition_state tool enum
VALID_TRANSITIONS: dict[str, list[str]] = {
    "PRE_TRIAGE":    ["TRIAGE", "SUPPRESSED", "ESCALATING"],
    "TRIAGE":        ["INVESTIGATING", "ESCALATING"],
    "INVESTIGATING": ["HYPOTHESIZING", "ESCALATING"],
    "HYPOTHESIZING": ["REMEDIATING", "ESCALATING"],
    "REMEDIATING":   ["RESOLVED", "ESCALATING"],
    "ESCALATING":    ["RESOLVED"],
}

# Terminal states — FSM loop exits when these are reached
TERMINAL_STATES = frozenset({"RESOLVED", "SUPPRESSED", "ESCALATING"})

# Deterministic, low-blast-radius root causes that qualify for auto-remediation.
# Anything outside this set routes to ESCALATING — unknown always escalates.
_SAFE_REMEDIATION_PATTERNS = frozenset({
    "keepalive_timeout",
    "interface_flap",
    "config_drift",
    "hardware_error",
    "mtu_mismatch",
    "duplex_mismatch",
    "bgp_hold_timer",
})


def decide_next_state(hypothesis: dict) -> tuple[str, str]:
    """Route the FSM from HYPOTHESIZING to REMEDIATING or ESCALATING.

    ESCALATING triggers when ANY of:
    - Single source IP >60% of egress (potential exfiltration / DDoS)
    - Distinct destination IPs >500 (high port spread / scanning)
    - Source IP matches a threat intel indicator
    - Confidence <0.70 (ambiguous evidence)

    REMEDIATING triggers when ALL of:
    - is_security_threat is False
    - root_cause is a known-safe deterministic pattern
    - confidence >= 0.90
    - No concurrent anomalies on related interfaces

    Args:
        hypothesis: dict with keys egress_pct, distinct_dst_ips,
            threat_intel_hit, confidence, is_security_threat,
            root_cause, concurrent_anomalies.

    Returns:
        (next_state, reason) where next_state is "REMEDIATING" or "ESCALATING".
    """
    egress_pct       = float(hypothesis.get("egress_pct", 0.0))
    distinct_dst     = int(hypothesis.get("distinct_dst_ips", 0))
    threat_intel_hit = bool(hypothesis.get("threat_intel_hit", False))
    confidence       = float(hypothesis.get("confidence", 0.0))
    is_security      = bool(hypothesis.get("is_security_threat", False))
    root_cause       = str(hypothesis.get("root_cause", "")).lower().strip()
    concurrent       = bool(hypothesis.get("concurrent_anomalies", False))

    # ── ESCALATING triggers (any one is sufficient) ───────────────────────────
    if egress_pct > 60.0:
        return (
            "ESCALATING",
            f"Single source accounts for {egress_pct:.1f}% of egress "
            f"(threshold 60%) — potential exfiltration or DDoS.",
        )

    if distinct_dst > 500:
        return (
            "ESCALATING",
            f"High port spread: {distinct_dst} distinct destination IPs "
            "observed — consistent with scanning or data exfiltration.",
        )

    if threat_intel_hit:
        return (
            "ESCALATING",
            "Source IP matched a known threat intelligence indicator — "
            "immediate escalation required.",
        )

    if confidence < 0.70:
        return (
            "ESCALATING",
            f"Confidence {confidence:.2f} below threshold 0.70 — "
            "ambiguous evidence, escalate for human review.",
        )

    # ── REMEDIATING gate (all conditions must hold) ───────────────────────────
    if (
        not is_security
        and root_cause in _SAFE_REMEDIATION_PATTERNS
        and confidence >= 0.90
        and not concurrent
    ):
        return (
            "REMEDIATING",
            f"Root cause '{root_cause}' is deterministic and low-risk "
            f"(confidence {confidence:.2f}, no concurrent anomalies, "
            "no security indicators) — safe to auto-remediate.",
        )

    # ── Default: ambiguous → escalate ─────────────────────────────────────────
    return (
        "ESCALATING",
        f"Root cause '{root_cause}' did not satisfy auto-remediation criteria "
        f"(security={is_security}, confidence={confidence:.2f}, "
        f"concurrent_anomalies={concurrent}) — escalate for human review.",
    )
