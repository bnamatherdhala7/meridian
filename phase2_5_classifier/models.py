"""Data models for the Alert Classifier."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RoutingTier(str, Enum):
    HIGH   = "HIGH"    # ≥0.75 confidence → immediate FSM investigation
    MEDIUM = "MEDIUM"  # 0.40–0.74 → human review queue
    LOW    = "LOW"     # <0.40 → suppressed (logged, not investigated)


@dataclass
class Alert:
    """A single Splunk notable event or risk-based alert."""
    alert_id:    str
    timestamp:   str           # ISO-8601
    device_id:   str
    src_ip:      str = ""
    severity:    str = "medium"  # low / medium / high / critical
    rule_name:   str = ""
    description: str = ""
    raw_fields:  dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertCluster:
    """A group of alerts that share at least one indicator (device, IP, or time window)."""
    cluster_id:    str
    alerts:        list[Alert]
    shared_device: str = ""
    shared_src_ip: str = ""
    time_span_min: float = 0.0   # duration from first to last alert in minutes
    max_severity:  str = "medium"

    @property
    def alert_count(self) -> int:
        return len(self.alerts)

    @property
    def distinct_rules(self) -> list[str]:
        return list({a.rule_name for a in self.alerts if a.rule_name})

    @property
    def corroboration_score(self) -> float:
        """Simple heuristic: more distinct rules = stronger signal."""
        return min(1.0, len(self.distinct_rules) / 5.0)


@dataclass
class RoutingDecision:
    """Output of the classifier for a single cluster."""
    cluster_id:    str
    tier:          RoutingTier
    confidence:    float          # 0.0–1.0
    reason:        str
    key_evidence:  list[str]
    suggested_action: str
    token_cost:    int = 0
    # If tier == HIGH, this is the scenario dict to pass to Phase 2 FSM
    fsm_scenario:  dict[str, Any] = field(default_factory=dict)
