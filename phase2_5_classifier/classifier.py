"""Alert Classifier — clusters correlated alerts and scores each cluster once.

Design principles:
- Clustering is deterministic (rules-based). No LLM involved.
- Scoring is one Claude call per cluster (~300 tokens), not a full FSM loop.
- The LLM's only job: given pre-grouped signals, assess noise vs. real threat.
- Output is always structured JSON so routing is machine-readable.
"""
from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone

import anthropic

from phase2_5_classifier.models import (
    Alert, AlertCluster, RoutingDecision, RoutingTier,
)

# ── Routing thresholds ────────────────────────────────────────────────────────
_HIGH_THRESHOLD   = 0.75   # → immediate FSM investigation
_MEDIUM_THRESHOLD = 0.40   # → human review queue; below → suppressed

# ── Cluster parameters ────────────────────────────────────────────────────────
_CLUSTER_WINDOW_MIN = 15   # alerts within 15 minutes on the same device cluster together

# ── Scoring prompt ────────────────────────────────────────────────────────────
_SYSTEM = """\
You are a SOC alert triage engine. You receive a cluster of correlated security alerts
from Splunk and must determine whether they represent a real threat or noise.

Respond ONLY with a valid JSON object — no prose, no markdown fences:
{
  "confidence": 0.0-to-1.0,
  "tier": "HIGH | MEDIUM | LOW",
  "reason": "one sentence explaining the decision",
  "key_evidence": ["array of specific facts that drove the decision"],
  "suggested_action": "action verb + specific target (e.g. Investigate src_ip 10.x.x.x)"
}

Confidence calibration:
  HIGH (≥0.75): multiple distinct rule types firing, specific IOCs present, anomalous values
  MEDIUM (0.40–0.74): single rule type, plausible but unconfirmed, ambiguous context
  LOW (<0.40): single low-severity rule, common benign pattern, no specific IOCs

Rules:
- confidence must be a number between 0.0 and 1.0
- tier must match the confidence band above
- key_evidence must list specific values (IPs, counts, percentages) not generic statements
- suggested_action must start with an action verb"""


class AlertClassifier:
    def __init__(self, model: str = "claude-sonnet-4-6") -> None:
        self.client = anthropic.Anthropic()
        self.model  = model

    # ── Public API ────────────────────────────────────────────────────────────

    def classify(self, alerts: list[Alert]) -> list[RoutingDecision]:
        """Cluster alerts then score each cluster. Returns one decision per cluster."""
        clusters  = self._cluster(alerts)
        decisions = [self._score_cluster(c) for c in clusters]
        return decisions

    def classify_single(self, alert: Alert) -> RoutingDecision:
        """Convenience wrapper for a single alert."""
        return self.classify([alert])[0]

    # ── Clustering (deterministic, no LLM) ───────────────────────────────────

    def _cluster(self, alerts: list[Alert]) -> list[AlertCluster]:
        """Group alerts by shared device + 15-minute time window.

        Two alerts belong to the same cluster if they share a device_id AND
        their timestamps are within _CLUSTER_WINDOW_MIN of each other.
        If src_ip also matches, that strengthens the cluster (but is not required).
        """
        if not alerts:
            return []

        sorted_alerts = sorted(alerts, key=lambda a: a.timestamp)
        clusters: list[AlertCluster] = []
        used: set[str] = set()

        for seed in sorted_alerts:
            if seed.alert_id in used:
                continue

            group = [seed]
            used.add(seed.alert_id)
            seed_ts = _parse_ts(seed.timestamp)

            for other in sorted_alerts:
                if other.alert_id in used:
                    continue
                if other.device_id != seed.device_id:
                    continue
                other_ts = _parse_ts(other.timestamp)
                if abs((other_ts - seed_ts).total_seconds()) <= _CLUSTER_WINDOW_MIN * 60:
                    group.append(other)
                    used.add(other.alert_id)

            shared_ip = seed.src_ip if all(a.src_ip == seed.src_ip for a in group if a.src_ip) else ""
            severities = ["low", "medium", "high", "critical"]
            max_sev = max((a.severity for a in group), key=lambda s: severities.index(s) if s in severities else 0)
            times = [_parse_ts(a.timestamp) for a in group]
            span = (max(times) - min(times)).total_seconds() / 60.0

            clusters.append(AlertCluster(
                cluster_id    = f"CLU-{uuid.uuid4().hex[:8].upper()}",
                alerts        = group,
                shared_device = seed.device_id,
                shared_src_ip = shared_ip,
                time_span_min = round(span, 1),
                max_severity  = max_sev,
            ))

        return clusters

    # ── Scoring (single LLM call per cluster) ─────────────────────────────────

    def _score_cluster(self, cluster: AlertCluster) -> RoutingDecision:
        prompt = _build_prompt(cluster)

        response = self.client.messages.create(
            model      = self.model,
            max_tokens = 512,
            system     = _SYSTEM,
            messages   = [{"role": "user", "content": prompt}],
        )

        tokens = response.usage.input_tokens + response.usage.output_tokens
        raw = response.content[0].text.strip()
        # Strip markdown fences if the model wraps output despite instructions
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            # Fallback: treat as HIGH so nothing gets silently dropped
            parsed = {
                "confidence": 0.80,
                "tier": "HIGH",
                "reason": "JSON parse error — defaulting to HIGH to avoid suppression",
                "key_evidence": [raw[:200]],
                "suggested_action": f"Investigate {cluster.shared_device}",
            }

        confidence = float(parsed.get("confidence", 0.5))
        tier_str   = parsed.get("tier", "").upper()

        # Enforce consistency between confidence and tier
        if confidence >= _HIGH_THRESHOLD:
            tier = RoutingTier.HIGH
        elif confidence >= _MEDIUM_THRESHOLD:
            tier = RoutingTier.MEDIUM
        else:
            tier = RoutingTier.LOW

        fsm_scenario: dict = {}
        if tier == RoutingTier.HIGH:
            fsm_scenario = _build_fsm_scenario(cluster, parsed)

        return RoutingDecision(
            cluster_id       = cluster.cluster_id,
            tier             = tier,
            confidence       = round(confidence, 3),
            reason           = parsed.get("reason", ""),
            key_evidence     = parsed.get("key_evidence", []),
            suggested_action = parsed.get("suggested_action", ""),
            token_cost       = tokens,
            fsm_scenario     = fsm_scenario,
        )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_ts(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def _build_prompt(cluster: AlertCluster) -> str:
    lines = [
        f"Cluster ID: {cluster.cluster_id}",
        f"Device: {cluster.shared_device}",
        f"Alert count: {cluster.alert_count}",
        f"Time span: {cluster.time_span_min} minutes",
        f"Max severity: {cluster.max_severity}",
        f"Distinct rule types ({len(cluster.distinct_rules)}): {', '.join(cluster.distinct_rules)}",
    ]
    if cluster.shared_src_ip:
        lines.append(f"Shared src_ip: {cluster.shared_src_ip}")

    lines.append("\nAlerts:")
    for a in cluster.alerts:
        lines.append(f"  [{a.severity.upper()}] {a.rule_name}: {a.description}")
        for k, v in list(a.raw_fields.items())[:4]:
            lines.append(f"    {k}={v}")

    return "\n".join(lines)


def _build_fsm_scenario(cluster: AlertCluster, scored: dict) -> dict:
    """Build a Phase 2 FSM scenario dict from a HIGH-confidence cluster."""
    first = cluster.alerts[0]
    return {
        "incident_id":  f"INC-{cluster.cluster_id}",
        "title":        f"{cluster.alert_count} correlated alerts on {cluster.shared_device}",
        "description":  scored.get("reason", "Correlated alert cluster"),
        "device":       cluster.shared_device,
        "interface":    first.raw_fields.get("interface", "unknown"),
        "site":         first.raw_fields.get("site", "unknown"),
        "severity":     "P1" if cluster.max_severity == "critical" else "P2",
        "reported_at":  first.timestamp,
        "classifier": {
            "cluster_id":  cluster.cluster_id,
            "confidence":  scored.get("confidence"),
            "alert_count": cluster.alert_count,
            "key_evidence": scored.get("key_evidence", []),
        },
    }
