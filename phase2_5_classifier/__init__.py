"""Phase 2.5 — Alert Classifier.

Pre-filter layer between Splunk notables and the Phase 2 FSM investigator.
Clusters correlated alerts, scores each cluster with a single LLM call,
and routes only high-confidence clusters to full FSM investigation.

Flow:
    Raw Splunk alerts
        → cluster()          # deterministic rules, no LLM
        → score_cluster()    # single Claude call per cluster (~300 tokens)
        → RoutingDecision    # HIGH / MEDIUM / LOW
            HIGH  → Phase 2 FSM investigation
            MEDIUM → human review queue
            LOW    → suppressed (logged, not investigated)

Expected impact: 40-50% reduction in FSM investigations triggered.
"""
from phase2_5_classifier.classifier import AlertClassifier
from phase2_5_classifier.models import Alert, AlertCluster, RoutingDecision, RoutingTier

__all__ = ["AlertClassifier", "Alert", "AlertCluster", "RoutingDecision", "RoutingTier"]
