"""Unit tests for vigil.mcp_client — mock CI tools only (no real MCP calls)."""
import pytest
import os

os.environ.setdefault("SPLUNK_URL",      "https://mock.splunkcloud.com")
os.environ.setdefault("SPLUNK_TOKEN",    "mock-token")
os.environ.setdefault("SPLUNK_MCP_URL",  "https://mock.splunkcloud.com/services/mcp")
os.environ.setdefault("PINECONE_API_KEY",        "mock-pinecone-key")
os.environ.setdefault("PINECONE_SPL_INDEX",      "vigil-spl-knowledge")
os.environ.setdefault("PINECONE_INCIDENT_INDEX", "vigil-incident-memory")
os.environ.setdefault("PINECONE_ENVIRONMENT",    "us-east-1")
os.environ.setdefault("OPENAI_API_KEY",   "mock-openai-key")
os.environ.setdefault("ANTHROPIC_API_KEY","mock-anthropic-key")

from vigil.mcp_client import get_network_topology, get_telemetry_metrics


def test_mock_topology_known_device():
    result = get_network_topology("sw-core-01")
    assert result["blast_radius"] == "HIGH"
    assert result["downstream_count"] == 14


def test_mock_topology_unknown_device():
    result = get_network_topology("unknown-device-99")
    assert result["blast_radius"] == "UNKNOWN"
    assert result["downstream_count"] == 0


def test_mock_telemetry_known_device():
    result = get_telemetry_metrics("sw-core-01")
    assert "cpu_pct" in result
    assert result["cpu_pct"] == 34


def test_mock_telemetry_unknown_device():
    result = get_telemetry_metrics("nonexistent-device")
    assert result["cpu_pct"] == 0
