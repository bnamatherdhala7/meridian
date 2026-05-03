"""Mocked SP MCP tools — same interface as real SP GA MCP server.

Swap mode to "live" in config.yaml + set SP_ENDPOINT + SP_TOKEN env vars
to connect to a real SP instance without changing any other code.
"""
from typing import Any

_INDEXES = [
    {"name": "network_telemetry", "size_mb": 45200, "event_count": 2847000,
     "earliest": "2024-01-01", "latest": "2024-02-14"},
    {"name": "security_logs", "size_mb": 12800, "event_count": 891000,
     "earliest": "2024-01-01", "latest": "2024-02-14"},
    {"name": "ise_logs", "size_mb": 3200, "event_count": 234000,
     "earliest": "2024-01-01", "latest": "2024-02-14"},
    {"name": "netflow", "size_mb": 78900, "event_count": 15600000,
     "earliest": "2024-01-01", "latest": "2024-02-14"},
]

_KNOWLEDGE_OBJECTS = [
    {"type": "saved_search", "name": "Interface Error Spike Alert",
     "search": "index=network_telemetry out_errors>1000"},
    {"type": "field_extraction", "name": "ci_interface_parser",
     "fields": ["device_id", "interface", "in_errors", "out_errors", "drops"]},
    {"type": "lookup", "name": "device_inventory",
     "fields": ["device_id", "hostname", "site", "model"]},
]

_INTERFACE_RESULT = {
    "events": [
        {"_time": "2024-02-14T14:32:00Z", "device_id": "sj-catalyst-01", "interface": "GigE0/1",
         "in_errors": 12, "out_errors": 2847, "drops": 1923, "utilization_pct": 94.2, "vlan": 100},
        {"_time": "2024-02-14T14:30:00Z", "device_id": "sj-catalyst-01", "interface": "GigE0/1",
         "in_errors": 8, "out_errors": 2634, "drops": 1701, "utilization_pct": 91.8, "vlan": 100},
        {"_time": "2024-02-14T14:28:00Z", "device_id": "sj-catalyst-01", "interface": "GigE0/1",
         "in_errors": 5, "out_errors": 312, "drops": 89, "utilization_pct": 42.1, "vlan": 100},
    ],
    "stats": {
        "avg_out_errors": 1931, "avg_drops": 1238,
        "spike_at": "2024-02-14T14:30:00Z", "duration_mins": 4,
        "note": "Asymmetric error pattern: out_errors >> in_errors suggests egress congestion"
    },
}

_EGRESS_RESULT = {
    "events": [
        {"src_ip": "10.14.22.87", "bytes_out": 8947234, "pct_of_egress": 71.2,
         "dest_ip_count": 847, "protocol": "TCP", "port_spread": "high"},
        {"src_ip": "10.14.22.12", "bytes_out": 1203847, "pct_of_egress": 9.6,
         "dest_ip_count": 12, "protocol": "TCP"},
        {"src_ip": "10.14.22.45", "bytes_out": 987234, "pct_of_egress": 7.9,
         "dest_ip_count": 8, "protocol": "UDP"},
    ],
    "stats": {
        "total_bytes": 12567891, "top_src": "10.14.22.87", "top_src_pct": 71.2,
        "anomaly": "Single host accounts for 71.2% of egress — threshold is 60%"
    },
}


def run_spl_query(spl: str, index: str = "*", time_window: str = "last 30 minutes") -> dict[str, Any]:
    spl_lower = spl.lower()
    if any(k in spl_lower for k in ("out_errors", "in_errors", "drops", "gige0/1", "interface")):
        return {"query": spl, **_INTERFACE_RESULT}
    if any(k in spl_lower for k in ("src_ip", "bytes_out", "egress", "netflow")):
        return {"query": spl, **_EGRESS_RESULT}
    return {"query": spl, "events": [], "stats": {"message": "No events matched."}}


def generate_spl(natural_language: str, index: str = "network_telemetry") -> dict[str, Any]:
    nl = natural_language.lower()
    if any(k in nl for k in ("error", "drop", "packet loss", "interface", "gige")):
        return {
            "spl": (
                f'index={index} device_id="sj-catalyst-01" interface="GigE0/1" '
                f'| stats avg(out_errors) as avg_errors, avg(drops) as avg_drops by _time span=2m '
                f'| where avg_errors > 100'
            ),
            "explanation": "Queries interface error counters aggregated in 2-minute buckets, filtered to anomalous levels.",
            "estimated_events": 1200,
        }
    if any(k in nl for k in ("traffic", "egress", "src_ip", "bandwidth")):
        return {
            "spl": (
                'index=netflow device_id="sj-catalyst-01" interface="GigE0/1" direction=egress '
                '| stats sum(bytes_out) as bytes_out by src_ip '
                '| eval pct_of_egress=round(bytes_out/sum(bytes_out)*100,1) | sort -bytes_out'
            ),
            "explanation": "Aggregates egress traffic by source IP to identify dominant talkers.",
            "estimated_events": 340,
        }
    return {
        "spl": f"index={index} | head 100",
        "explanation": "General query — refine with specific fields.",
        "estimated_events": 100,
    }


def search_indexes(query: str = "") -> dict[str, Any]:
    return {"indexes": _INDEXES, "total": len(_INDEXES)}


def get_knowledge_objects(object_type: str = "all") -> dict[str, Any]:
    return {"objects": _KNOWLEDGE_OBJECTS, "total": len(_KNOWLEDGE_OBJECTS)}
