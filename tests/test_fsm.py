"""Unit tests for vigil.fsm — classifier gate and suppression logic."""
import pytest
from vigil.classifier import classify


def test_classify_suppresses_test_alert():
    ok, score, reason = classify("test alert only")
    assert not ok
    assert "test_alert" in reason


def test_classify_suppresses_maintenance():
    ok, score, reason = classify("during maintenance window — no action needed")
    assert not ok
    assert "maintenance_suppressed" in reason


def test_classify_passes_cpu_spike():
    ok, score, reason = classify("CPU 94% on core device for 12 minutes — unknown process")
    assert ok
    assert reason == "proceed_to_fsm"


def test_classify_passes_exfil():
    ok, score, reason = classify("high egress concentration — possible exfil pattern 78% single source")
    assert ok


def test_classify_below_threshold():
    ok, score, reason = classify("minor interface counter increment — low signal")
    assert not ok
    assert reason == "below_threshold"
